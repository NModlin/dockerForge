"""
Docker daemon configuration schemas for the DockerForge Web UI.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class RegistryConfig(BaseModel):
    """Registry configuration schema."""
    registry_mirrors: List[str] = Field(
        default_factory=list,
        description="Registry mirrors",
        alias="registry-mirrors"
    )
    insecure_registries: List[str] = Field(
        default_factory=list,
        description="Insecure registries",
        alias="insecure-registries"
    )
    allow_nondistributable_artifacts: List[str] = Field(
        default_factory=list,
        description="Registries for which nondistributable artifacts are allowed",
        alias="allow-nondistributable-artifacts"
    )

    class Config:
        allow_population_by_field_name = True


class LoggingConfig(BaseModel):
    """Logging configuration schema."""
    log_driver: str = Field(
        default="json-file",
        description="Logging driver",
        alias="log-driver"
    )
    log_opts: Dict[str, str] = Field(
        default_factory=dict,
        description="Logging driver options",
        alias="log-opts"
    )

    class Config:
        allow_population_by_field_name = True


class StorageConfig(BaseModel):
    """Storage configuration schema."""
    storage_driver: Optional[str] = Field(
        default=None,
        description="Storage driver",
        alias="storage-driver"
    )
    storage_opts: List[str] = Field(
        default_factory=list,
        description="Storage driver options",
        alias="storage-opts"
    )
    data_root: Optional[str] = Field(
        default=None,
        description="Docker data root directory",
        alias="data-root"
    )

    class Config:
        allow_population_by_field_name = True


class AddressPool(BaseModel):
    """Address pool configuration schema."""
    base: str = Field(..., description="Base CIDR")
    size: int = Field(..., description="Subnet size")


class NetworkConfig(BaseModel):
    """Network configuration schema."""
    default_address_pools: List[AddressPool] = Field(
        default_factory=list,
        description="Default address pools for networks",
        alias="default-address-pools"
    )
    dns: List[str] = Field(
        default_factory=list,
        description="DNS servers"
    )
    dns_opts: List[str] = Field(
        default_factory=list,
        description="DNS options",
        alias="dns-opts"
    )
    dns_search: List[str] = Field(
        default_factory=list,
        description="DNS search domains",
        alias="dns-search"
    )
    bip: Optional[str] = Field(
        default=None,
        description="Docker bridge IP"
    )
    fixed_cidr: Optional[str] = Field(
        default=None,
        description="Fixed CIDR",
        alias="fixed-cidr"
    )
    fixed_cidr_v6: Optional[str] = Field(
        default=None,
        description="Fixed CIDR for IPv6",
        alias="fixed-cidr-v6"
    )
    default_gateway: Optional[str] = Field(
        default=None,
        description="Default gateway",
        alias="default-gateway"
    )
    default_gateway_v6: Optional[str] = Field(
        default=None,
        description="Default gateway for IPv6",
        alias="default-gateway-v6"
    )
    ip_forward: Optional[bool] = Field(
        default=None,
        description="IP forwarding",
        alias="ip-forward"
    )
    ip_masq: Optional[bool] = Field(
        default=None,
        description="IP masquerading",
        alias="ip-masq"
    )
    iptables: Optional[bool] = Field(
        default=None,
        description="Enable iptables",
        alias="iptables"
    )
    ipv6: Optional[bool] = Field(
        default=None,
        description="Enable IPv6"
    )

    class Config:
        allow_population_by_field_name = True


class DaemonConfig(BaseModel):
    """Complete Docker daemon configuration schema."""
    registry: RegistryConfig = Field(default_factory=RegistryConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    network: NetworkConfig = Field(default_factory=NetworkConfig)


class DriverInfo(BaseModel):
    """Driver information schema."""
    name: str = Field(..., description="Driver name")
    description: str = Field(..., description="Driver description")


class AvailableDrivers(BaseModel):
    """Available drivers schema."""
    logging_drivers: List[DriverInfo] = Field(..., description="Available logging drivers")
    storage_drivers: List[DriverInfo] = Field(..., description="Available storage drivers")


class ConfigUpdateResponse(BaseModel):
    """Configuration update response schema."""
    success: bool = Field(..., description="Whether the update was successful")
    message: str = Field(..., description="Response message")
    requires_restart: bool = Field(default=False, description="Whether a restart is required")
