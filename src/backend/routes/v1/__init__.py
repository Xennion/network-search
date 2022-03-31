from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import arrow

from schemas.network import NetworkSchema
from libs.network import NetworkDevice
from libs.common import merge_networks
from libs.config import config
from libs.db import NetworkDatabaseModel, SessionLocal, engine, Base

Base.metadata.create_all(bind=engine)

v1_router = APIRouter()

state = {
    "last_poll": None,
    "ssh_poll_minimum_seconds": config["ssh_poll_minimum_seconds"]
    if config.get("ssh_poll_minimum_seconds")
    else 60,
}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# response_model=list[NetworkSchema]
@v1_router.get("/networks")
def get_all_networks(db: Session = Depends(get_db)):
    """
    Gets all networks from DB
    """
    return db.query(NetworkDatabaseModel).all()


@v1_router.get("/poll")
def poll_all(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Polls all networks to be updated in database and returns if polls initiated successfully
    """

    # check if last poll > configured minimum poll interval
    if (
        state.get("last_poll")
        and state["last_poll"].shift(seconds=state["ssh_poll_minimum_seconds"])
        > arrow.utcnow()
    ):
        raise HTTPException(
            status_code=429,
            detail=f"RATE LIMIT ERROR: Polling allowed again {state['last_poll'].shift(seconds=state['ssh_poll_minimum_seconds']).humanize()}",
        )

    dc_names = [dc["name"] for dc in config["datacenters"]]
    for dc in dc_names:
        dc = dc.upper()
        background_tasks.add_task(poll, dc, db=db, timeout=60)

    state["last_poll"] = arrow.utcnow()
    return {"status": "poll initiated successfully", "datacenters": dc_names}


@v1_router.get("/poll/{datacenter}", response_model=list[NetworkSchema])
def poll(datacenter, db: Session = Depends(get_db), timeout=None):
    datacenter = datacenter.upper()
    """
    Used to sychronously poll a datacenter for testing / debug
    Does not store result in DB
    """

    device_username = config["auth"]["user"]
    device_password = config["auth"]["pass"]

    # check for referenced datacenter in config and raise if not found
    dc = [dc for dc in config["datacenters"] if dc["name"] == datacenter]
    if not dc:
        raise HTTPException(404, detail=f"Datacenter {datacenter} not found")

    devices = dc[0]["devices"]
    api_result = []
    for device in devices:
        # check to see if auth is overriden at the device level
        if "auth" in device:
            device_username = device["auth"]["user"]
            device_password = device["auth"]["pass"]

        # call proper underlying parser module
        # this should just dynamically infer possible types from files in this directory and
        # then raise if not a valid device_type
        connection = NetworkDevice(
            datacenter=datacenter,
            host=device["name"],
            device_type=device["type"],
            username=device_username,
            password=device_password,
        )

        device_result = connection.get_data()

        # merge data
        api_result = merge_networks(api_result, device_result)

    # delete all rows related to {datacenter}
    db.query(NetworkDatabaseModel).filter(
        NetworkDatabaseModel.datacenter == datacenter
    ).delete()
    db.commit()

    # add new rows
    models = [NetworkDatabaseModel(**network) for network in api_result]
    db.add_all(models)
    db.commit()

    print(f"Stored {len(api_result)} rows in database for DC: {datacenter}")
    return api_result


@v1_router.get("/health")
def health(db: Session = Depends(get_db)):
    # things that would synthetically test the app works
    # query a database table for a row
    return {"message": "looks good"}
