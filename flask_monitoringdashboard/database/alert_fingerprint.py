from sqlalchemy.exc import IntegrityError

from flask_monitoringdashboard.database import AlertFingerprint, DBSession


def claim_alert_fingerprint(fingerprint: str) -> bool:
    """
    Record that an alert is being sent for this fingerprint.
    Uses its own session (not the thread-local scoped one), so it commits independently of
    the caller's transaction.
    :return: True if the fingerprint was not seen before, i.e. the caller should send the alert.
    """
    session = DBSession()
    try:
        if session.get(AlertFingerprint, fingerprint) is not None:
            return False
        session.add(AlertFingerprint(hash=fingerprint))
        session.commit()
        return True
    except IntegrityError:
        # another worker inserted the same fingerprint between our check and our commit
        session.rollback()
        return False
    finally:
        session.close()
