"""
Tasks package for PIDL Research System
6 blockchain eğitim görevi
"""
from .task1_diploma import Task1Diploma
from .task2_nft import Task2NFT
from .task3_access import Task3Access
from .task4_loan import Task4Loan
from .task5_incentive import Task5Incentive
from .task6_dao import Task6DAO

# Tüm görevleri liste olarak
ALL_TASKS = [
    Task1Diploma,
    Task2NFT,
    Task3Access,
    Task4Loan,
    Task5Incentive,
    Task6DAO
]


def get_task_by_number(task_number: int):
    """Görev numarasına göre task sınıfını döndür"""
    if 1 <= task_number <= 6:
        return ALL_TASKS[task_number - 1]()
    else:
        raise ValueError(f"Invalid task number: {task_number}. Must be 1-6.")


__all__ = [
    'Task1Diploma',
    'Task2NFT',
    'Task3Access',
    'Task4Loan',
    'Task5Incentive',
    'Task6DAO',
    'ALL_TASKS',
    'get_task_by_number'
]
