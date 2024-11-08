from typing import List
from dataclasses import dataclass


@dataclass(frozen=True)
class Proxy:
    ip: str
    port: str
    username: str
    password: str

    @classmethod
    def from_txt(cls, file_path: str) -> List["Proxy"]:
        """Читает данные прокси из текстового файла и создает экземпляры класса Proxy"""
        proxies = []
        with open(file_path, "r") as f:
            for line in f:
                print(line.strip().split(":"))
                ip, port, username, password = line.strip().split(":")
                proxies.append(cls(ip, port, username, password))
        return proxies

    def __str__(self):
        """Возвращаем строковое представление прокси"""
        return f"{self.ip}:{self.port} (User: {self.username}, Pass: {self.password})"


class User:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password

    @classmethod
    def from_txt(cls, file_path: str) -> List["User"]:
        """Читает данные пользователей из текстового файла и создает экземпляры класса User"""
        users = []
        with open(file_path, "r") as f:
            for line in f:
                email, password = line.strip().split(":")
                users.append(cls(email, password))
        return users

    def __str__(self):
        """Метод __str__ для строкового представления пользователя."""
        return f"Email: {self.email}, Password: {self.password}"
