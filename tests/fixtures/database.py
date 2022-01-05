import pytest

try:
    from sqlalchemy.orm import scoped_session
    from factory.alchemy import SQLAlchemyModelFactory
    from flask_monitoringdashboard.database import DBSession

    @pytest.fixture
    def session():
        """Db session."""
        session = scoped_session(DBSession)
        yield session
        session.close()


    class ModelFactory(SQLAlchemyModelFactory):
        """Base model factory."""

        class Meta:
            abstract = True
            sqlalchemy_session = scoped_session(DBSession)
            sqlalchemy_session_persistence = 'commit'
except ImportError:
    from factory import base

    class SQLAlchemyOptions(base.FactoryOptions):
        def _check_sqlalchemy_session_persistence(self, meta, value):
            pass

        def _check_force_flush(self, meta, value):
            pass

        def _build_default_options(self):
            return super(SQLAlchemyOptions, self)._build_default_options() + [
                base.OptionDefault('sqlalchemy_session', None, inherit=True),
                base.OptionDefault(
                    'sqlalchemy_session_persistence',
                    None,
                    inherit=True,
                    checker=self._check_sqlalchemy_session_persistence,
                ),
                # DEPRECATED as of 2.8.0, remove in 3.0.0
                base.OptionDefault(
                    'force_flush',
                    False,
                    inherit=True,
                    checker=self._check_force_flush,
                )
            ]


    class SQLAlchemyModelFactory(base.Factory):
        """Factory for SQLAlchemy models. """

        _options_class = SQLAlchemyOptions

        class Meta:
            abstract = True

        @classmethod
        def _create(cls, model_class, *args, **kwargs):
            """Create an instance of the model, and save it to the database."""
            session = cls._meta.sqlalchemy_session
            session_persistence = cls._meta.sqlalchemy_session_persistence
            if cls._meta.force_flush:
                session_persistence = "flush"

            obj = model_class(**kwargs)
            if session is None:
                raise RuntimeError("No session provided.")
            collection = obj.get_collection(session)
            if session_persistence == "commit":
                collection.insert_one(obj)
            return obj

    def get_session():
        from flask_monitoringdashboard.database.data_base_queries.mongo_db_objects import db_connection
        return db_connection

    class ModelFactory(SQLAlchemyModelFactory):
        sqlalchemy_session = None
        sqlalchemy_session_persistence = None

        class Meta:
            abstract = True
            sqlalchemy_session = get_session()
            sqlalchemy_session_persistence = 'commit'

    @pytest.fixture
    def session():
        yield get_session()

