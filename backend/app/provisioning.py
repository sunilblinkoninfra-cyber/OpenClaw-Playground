import docker
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
import logging

from app.config import settings
from app.database import Container, User
from app.schemas import ContainerStatus, ProvisioningResponse

logger = logging.getLogger(__name__)


class DockerOrchestrator:
    """Manages Docker container provisioning and lifecycle."""
    
    def __init__(self):
        self.client = docker.from_env()
    
    def create_container(
        self, 
        user_id: str, 
        db: Session
    ) -> tuple[Container, Optional[str]]:
        """
        Create and start a Docker container for a user.
        
        Returns:
            (container_model, error_message)
        """
        try:
            # Generate subdomain
            subdomain = f"user-{user_id[:8]}"
            
            # Pull the openclaw image (assumes it's pre-built)
            image_name = f"{settings.DOCKER_REGISTRY}/openclaw:latest"
            logger.info(f"Pulling image: {image_name}")
            
            # Start container
            container = self.client.containers.run(
                image_name,
                name=f"openclaw-{user_id}",
                detach=True,
                ports={f"{settings.CONTAINER_PORT}/tcp": None},
                mem_limit=f"{settings.CONTAINER_MEMORY_MB}m",
                cpu_shares=settings.CONTAINER_CPU_SHARES,
                environment={
                    "USER_ID": user_id,
                    "ENVIRONMENT": settings.ENVIRONMENT
                }
            )
            
            logger.info(f"Container started: {container.id}")
            
            # Create database record
            port_mapping = container.ports.get(f"{settings.CONTAINER_PORT}/tcp")
            host_port = port_mapping[0]["HostPort"] if port_mapping else None
            
            db_container = Container(
                user_id=user_id,
                container_id=container.id,
                status="running",
                subdomain=subdomain,
                url=f"https://{subdomain}.openclaw.ai",
                started_at=datetime.utcnow()
            )
            db.add(db_container)
            db.commit()
            db.refresh(db_container)
            
            return db_container, None
            
        except Exception as e:
            logger.error(f"Failed to create container: {str(e)}")
            error_msg = f"Provisioning failed: {str(e)}"
            
            # Create failed record
            db_container = Container(
                user_id=user_id,
                status="error",
                error_message=error_msg
            )
            db.add(db_container)
            db.commit()
            
            return db_container, error_msg
    
    def stop_container(self, container_id: str) -> bool:
        """Stop and remove a container."""
        try:
            container = self.client.containers.get(container_id)
            container.stop()
            container.remove()
            logger.info(f"Container stopped: {container_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to stop container {container_id}: {str(e)}")
            return False
    
    def get_container_status(self, container_id: str) -> Optional[str]:
        """Get container status."""
        try:
            container = self.client.containers.get(container_id)
            return container.status
        except Exception as e:
            logger.error(f"Failed to get container status: {str(e)}")
            return None


async def provision_user_environment(
    user_id: str, 
    db: Session
) -> ProvisioningResponse:
    """
    Orchestrate the full provisioning workflow.
    """
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return ProvisioningResponse(
            user_id=user_id,
            status=ContainerStatus(
                status="error",
                error_message="User not found"
            )
        )
    
    # Check if user already has active container
    existing_container = db.query(Container).filter(
        Container.user_id == user_id,
        Container.status.in_(["running", "provisioning"])
    ).first()
    
    if existing_container:
        return ProvisioningResponse(
            user_id=user_id,
            status=ContainerStatus(
                status=existing_container.status,
                container_id=existing_container.container_id,
                subdomain=existing_container.subdomain,
                url=existing_container.url,
                created_at=existing_container.created_at
            ),
            trial_end=user.trial_end
        )
    
    # Provision new container
    orchestrator = DockerOrchestrator()
    db_container, error = orchestrator.create_container(user_id, db)
    
    return ProvisioningResponse(
        user_id=user_id,
        status=ContainerStatus(
            status=db_container.status,
            container_id=db_container.container_id,
            subdomain=db_container.subdomain,
            url=db_container.url,
            created_at=db_container.created_at,
            error_message=error
        ),
        trial_end=user.trial_end
    )


async def stop_user_environment(user_id: str, db: Session) -> bool:
    """Stop a user's environment."""
    container = db.query(Container).filter(
        Container.user_id == user_id,
        Container.status == "running"
    ).first()
    
    if not container:
        return False
    
    orchestrator = DockerOrchestrator()
    success = orchestrator.stop_container(container.container_id)
    
    if success:
        container.status = "stopped"
        container.stopped_at = datetime.utcnow()
        db.commit()
    
    return success
