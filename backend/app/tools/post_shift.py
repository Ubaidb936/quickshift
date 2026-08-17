from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.tools.base import BaseTool
from app.models.models import Shift


class PostShiftTool(BaseTool):
    name = "post_shift"
    description = "Post a new shift on behalf of the business so workers can find and apply to it."

    def __init__(self, db: AsyncSession, business_id: int):
        self.db = db
        self.business_id = business_id

    async def execute(
        self,
        position: str,
        num_workers: int = 1,
        pay_rate: float | None = None,
        duties: str | None = None,
        attire: str | None = None,
        start_time: str | None = None,   # ISO format: "2026-08-17T09:00:00"
        end_time: str | None = None,
    ) -> dict:
        shift = Shift(
            business_id=self.business_id,
            position=position,
            num_workers=num_workers,
            pay_rate=pay_rate,
            duties=duties,
            attire=attire,
            start_time=datetime.fromisoformat(start_time) if start_time else None,
            end_time=datetime.fromisoformat(end_time) if end_time else None,
            status="active",
        )
        self.db.add(shift)
        await self.db.commit()
        await self.db.refresh(shift)

        return {
            "success": True,
            "shift_id": shift.id,
            "position": shift.position,
            "num_workers": shift.num_workers,
            "pay_rate": shift.pay_rate,
            "start_time": start_time,
            "end_time": end_time,
            "status": shift.status,
        }

    def schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "position": {
                            "type": "string",
                            "description": "Job title / role e.g. Bartender, Line Cook, Event Staff",
                        },
                        "num_workers": {
                            "type": "integer",
                            "description": "Number of workers needed for this shift",
                        },
                        "pay_rate": {
                            "type": "number",
                            "description": "Hourly pay rate in USD",
                        },
                        "duties": {
                            "type": "string",
                            "description": "Description of duties and responsibilities",
                        },
                        "attire": {
                            "type": "string",
                            "description": "Required attire or dress code e.g. all black, business casual",
                        },
                        "start_time": {
                            "type": "string",
                            "description": "Shift start time in ISO format e.g. 2026-08-17T09:00:00",
                        },
                        "end_time": {
                            "type": "string",
                            "description": "Shift end time in ISO format e.g. 2026-08-17T17:00:00",
                        },
                    },
                    "required": ["position"],
                },
            },
        }
