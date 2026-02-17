from fastapi import Router

router = Router()

@router.get("/domains")
def get_domains():
    return {"domains": ["research", "analysis", "summarization"]}

