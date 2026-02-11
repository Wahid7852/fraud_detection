from fastapi import APIRouter, HTTPException
from typing import List
from app.models.models import Rule
from app.schemas.schemas import Rule as RuleSchema, RuleBase

router = APIRouter()

@router.get("/", response_model=List[RuleSchema])
async def get_rules():
    return await Rule.find_all().to_list()

@router.post("/", response_model=RuleSchema)
async def create_rule(rule: RuleBase):
    db_rule = Rule(**rule.dict())
    await db_rule.insert()
    return db_rule

@router.put("/{rule_id}", response_model=RuleSchema)
async def update_rule(rule_id: str, rule_update: RuleBase):
    db_rule = await Rule.get(rule_id)
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    # Update fields
    update_data = rule_update.dict()
    for key, value in update_data.items():
        setattr(db_rule, key, value)
        
    await db_rule.save()
    return db_rule

@router.delete("/{rule_id}")
async def delete_rule(rule_id: str):
    db_rule = await Rule.get(rule_id)
    if not db_rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    await db_rule.delete()
    return {"message": "Rule deleted"}
