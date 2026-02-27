from app.agents.base_agent import BaseAgent
from app.models.generated_content import GeneratedContent
from app import log_bus


class OutreachAgent(BaseAgent):
    """
    📧 Outreach Agent
    Creates hyper-personalized 5-touch email + LinkedIn sequences
    for product-qualified prospects. Sounds human, not templated.
    """
    AGENT_TYPE = "outreach"

    def generate_email_sequence(self, company_name: str, country: str,
                                 persona_name: str, pain_point: str,
                                 trigger_event: str, key_title: str,
                                 industry: str = "", cluster: str = "CLUSTER_A",
                                 qualification_score: int = 80,
                                 campaign_id: str = None) -> GeneratedContent:
        log_bus.emit("📧", f"Outreach Agent — writing 5-touch sequence for {company_name} ({country})…", "info")

        voice = {
            "SME": "Empathetic, direct, reassuring. Short sentences. Lead with their pain, not your product. CFO/Sustainability Manager audience.",
            "ADVISORY": "Peer-to-peer. Respect their expertise. Position Triple I as force multiplier. ESG Director/Partner audience.",
        }.get(persona_name, "Professional, empathetic, value-first B2B.")

        system = f"""You are a world-class B2B sales copywriter for ESG software outreach.
You write emails that feel genuinely human — researched, specific, empathetic. Never generic.
Voice: {voice}
Triple I: AI ESG & Carbon Reporting. Auto-translates ESRS↔ISSB↔GRI↔TCFD. 80% time saving. Audit-ready."""

        user = f"""Write a 5-touch outreach sequence for:
Company: {company_name} | Country: {country} | Title: {key_title}
Pain: {pain_point} | Trigger: {trigger_event} | Score: {qualification_score}/100

Each touch must feel hand-written and specific to THIS company.

Return JSON:
- sequence_strategy: narrative arc across 5 touches (2-3 sentences)
- touch_1: type="cold_email", timing="Day 1", subject_a, subject_b, body (150-200 words), ps_line, send_time
- touch_2: type="linkedin_connection", timing="Day 3", connection_note (300 chars max), fallback_email_subject, fallback_email_body
- touch_3: type="value_email", timing="Day 7", subject, body (share regulatory insight, 200 words)
- touch_4: type="case_study_email", timing="Day 14", subject, body (similar company success, 150 words)
- touch_5: type="breakup_email", timing="Day 21", subject, body (honest last try, 80 words)
- linkedin_message_sequence: array of 3 short LinkedIn DM follow-ups
- objection_handlers: object with keys too_expensive, not_a_priority, using_competitor, no_time — each 2-3 sentence reply
- call_opener: 30-second opener script if they book a call"""

        schema = {
            "type": "object",
            "properties": {
                "sequence_strategy": {"type": "string"},
                "touch_1": {"type": "object", "properties": {
                    "type": {"type": "string"}, "timing": {"type": "string"},
                    "subject_a": {"type": "string"}, "subject_b": {"type": "string"},
                    "body": {"type": "string"}, "ps_line": {"type": "string"}, "send_time": {"type": "string"}
                }, "required": ["type","timing","subject_a","subject_b","body","ps_line","send_time"], "additionalProperties": False},
                "touch_2": {"type": "object", "properties": {
                    "type": {"type": "string"}, "timing": {"type": "string"},
                    "connection_note": {"type": "string"}, "fallback_email_subject": {"type": "string"}, "fallback_email_body": {"type": "string"}
                }, "required": ["type","timing","connection_note","fallback_email_subject","fallback_email_body"], "additionalProperties": False},
                "touch_3": {"type": "object", "properties": {
                    "type": {"type": "string"}, "timing": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}
                }, "required": ["type","timing","subject","body"], "additionalProperties": False},
                "touch_4": {"type": "object", "properties": {
                    "type": {"type": "string"}, "timing": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}
                }, "required": ["type","timing","subject","body"], "additionalProperties": False},
                "touch_5": {"type": "object", "properties": {
                    "type": {"type": "string"}, "timing": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}
                }, "required": ["type","timing","subject","body"], "additionalProperties": False},
                "linkedin_message_sequence": {"type": "array", "items": {"type": "string"}},
                "objection_handlers": {"type": "object", "properties": {
                    "too_expensive": {"type": "string"}, "not_a_priority": {"type": "string"},
                    "using_competitor": {"type": "string"}, "no_time": {"type": "string"}
                }, "required": ["too_expensive","not_a_priority","using_competitor","no_time"], "additionalProperties": False},
                "call_opener": {"type": "string"}
            },
            "required": ["sequence_strategy","touch_1","touch_2","touch_3","touch_4","touch_5",
                         "linkedin_message_sequence","objection_handlers","call_opener"],
            "additionalProperties": False
        }

        result = self._call_model(system, user, "outreach_sequence", schema)
        data = result["content"]

        return self._save_content(
            campaign_id=campaign_id,
            content_type="outreach_sequence",
            headline=f"📧 5-Touch: {company_name} → {key_title}",
            body=data["sequence_strategy"],
            json_output=data,
            usage=result["usage"],
        )

    def generate_bulk_sequences(self, prospect_list_content_id: str,
                                 max_prospects: int = 5,
                                 campaign_id: str = None) -> list:
        log_bus.emit("⚡", f"Bulk Outreach — loading prospect list {prospect_list_content_id[:8]}…", "info")
        source = self.db.query(GeneratedContent).filter(
            GeneratedContent.id == prospect_list_content_id
        ).first()
        if not source:
            log_bus.emit("❌", "Prospect list not found", "error")
            raise ValueError("Prospect list not found")

        companies = source.json_output.get("prospect_companies", [])
        top = sorted(companies, key=lambda x: x.get("qualification_score", 0), reverse=True)[:max_prospects]
        log_bus.emit("📋", f"Writing sequences for top {len(top)} prospects…", "info")

        results = []
        for p in top:
            try:
                log_bus.emit("✍️", f"Writing sequence for {p.get('company_name', '?')}…", "info")
                rec = self.generate_email_sequence(
                    company_name=p.get("company_name", ""),
                    country=p.get("headquarters", ""),
                    persona_name="SME",
                    pain_point=p.get("pain_point", "ESG reporting complexity"),
                    trigger_event=p.get("trigger_event", "CSRD deadline approaching"),
                    key_title=(p.get("key_decision_makers") or ["Sustainability Manager"])[0],
                    industry=p.get("industry", ""),
                    qualification_score=p.get("qualification_score", 70),
                    campaign_id=campaign_id,
                )
                results.append({"company": p["company_name"], "content_id": str(rec.id), "status": "generated"})
            except Exception as e:
                results.append({"company": p.get("company_name", "?"), "error": str(e), "status": "failed"})
        return results
