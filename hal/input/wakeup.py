import os


class WakeUp:
    """Lets one thread wake another that is blocked in select().

    The waiting thread puts fileno() in its select(); another thread calls
    set() to wake it. set() and close() must be called from the same thread,
    and close() only after the waiting thread has ended.
    """

    def __init__(self) -> None:
        read_fd, write_fd = os.pipe()
        os.set_blocking(read_fd, False)
        os.set_blocking(write_fd, False)
        self._read_fd: int | None = read_fd
        self._write_fd: int | None = write_fd
    
    def fileno(self) -> int:
        if self._read_fd is None:
            raise ValueError("WakeUp is closed")
        return self._read_fd
    
    def set(self) -> None:
        if self._write_fd is None:
            return
        try:
            os.write(self._write_fd, b"x")
        except BlockingIOError:
            pass  # the pipe is full: a wake-up is already waiting to be read

    def close(self) -> None:
        for fd in (self._read_fd, self._write_fd):
            if fd is not None:
                os.close(fd)
        self._read_fd = None
        self._write_fd = None