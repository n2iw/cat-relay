from typing import Protocol, runtime_checkable

@runtime_checkable
class Client(Protocol):
    def __enter__(self) -> 'Client':
        ...
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        ...

    def close(self) -> None:
        ...
    
    def get_new_freq(self) -> int | None:
        ...
    
    def get_new_mode(self) -> str | None:
        ...
    
    def set_freq_mode(self, freq: int | None, mode: str | None) -> None:
        ...