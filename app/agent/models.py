from dataclasses import dataclass


@dataclass
class Finding : 
    path : str #I added this cuz I'm curious if it will help
    stLine  : int #Start line
    msg : str 
    severity : str
    check_id : str #Most important thing to send to the rag

@dataclass
class AuditResult:
    finding : Finding #Embeds findings into Audit so you dont have duplicate objs for the same thing
    relevant_chunks : list[str]
    explanation : str
    fix : str

