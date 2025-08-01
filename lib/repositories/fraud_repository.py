from sqlmodel import Session, SQLModel, create_engine, select

from lib.models import TransactionRecord


class FraudRepository:
    """
    Handles DB interactions for transaction predictions,
    using SQLModel + a single Engine/Session.
    """

    def __init__(self, database_url: str):
        """
        Initializes the repository with a database engine.

        Args:
            database_url (str): The database connection URL.
        """
        self._engine = create_engine(
            database_url,
            echo=False,
        )
        SQLModel.metadata.create_all(self._engine)

    def add(self, record: TransactionRecord) -> TransactionRecord:
        """
        Inserts a new TransactionRecord into the DB, commits,
        refreshes it with generated fields (id, predicted_at),
        and returns it.

        Args:
            record (TransactionRecord): The transaction record to insert.

        Returns:
            TransactionRecord: The inserted record with refreshed fields (id, predicted_at).
        """
        with Session(self._engine) as session:
            session.add(record)
            session.commit()
            session.refresh(record)
            return record

    def list_all(self) -> list[TransactionRecord]:
        """
        Returns every record in predicted_transactions, newest first.

        Returns:
            List[TransactionRecord]: List of all transaction records ordered by prediction time descending.
        """
        stmt = select(TransactionRecord).order_by(TransactionRecord.predicted_at.desc())
        with Session(self._engine) as session:
            return session.exec(stmt).all()
