"""
Database configuration and models
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.shared.config import settings

# Create database engine
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite configuration for development
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.DATABASE_ECHO,
    )
else:
    # PostgreSQL configuration for production
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        pool_pre_ping=True,
        pool_recycle=300,
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base model class
Base = declarative_base()

# Naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

Base.metadata = MetaData(naming_convention=convention)


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db():
    """Initialize database and create tables"""
    # Import all models to ensure they are registered
    from backend.services.auth.models import User
    from backend.services.products.models import Product, Category, Brand
    from backend.services.inventory.models import Inventory, PriceHistory, Vendor
    from backend.services.orders.models import Order, OrderItem
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database initialized with SQLite")


class DatabaseManager:
    """Database management utilities"""
    
    @staticmethod
    def get_session():
        """Get a new database session"""
        return SessionLocal()
    
    @staticmethod
    def create_tables():
        """Create all database tables"""
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def drop_tables():
        """Drop all database tables"""
        Base.metadata.drop_all(bind=engine)
    
    @staticmethod
    def reset_database():
        """Reset database by dropping and recreating all tables"""
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
