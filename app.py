# app.py - Simplified AI Meeting Summarizer (Works without complex dependencies)

import re
import json
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass
import streamlit as st

@dataclass
class ActionItem:
    task: str
    assignee: str
    deadline: str
    priority: str

@dataclass
class MeetingSummary:
    title: str
    date: str
    participants: List[str]
    summary: str
    key_points: List[str]
    action_items: List[ActionItem]
    next_meeting: str

class SimpleMeetingSummarizer:
    def __init__(self):
        # No external dependencies required
        pass
    
    def extract_participants(self, transcript: str) -> List[str]:
        """Extract participant names from transcript"""
        # Look for speaker patterns like "John:", "Sarah said", etc.
        speaker_patterns = [
            r'([A-Z][a-z]+):\s',  # "John: "
            r'([A-Z][a-z]+)\s+said',  # "John said"
            r'([A-Z][a-z]+)\s+mentioned',  # "John mentioned"
            r'([A-Z][a-z]+)\s+asked',  # "John asked"
            r'([A-Z][a-z]+)\s+replied',  # "John replied"
        ]
        
        participants = set()
        for pattern in speaker_patterns:
            matches = re.findall(pattern, transcript)
            participants.update(matches)
        
        return list(participants)
    
    def generate_summary(self, transcript: str) -> str:
        """Generate meeting summary using simple text processing"""
        # Split into sentences
        sentences = re.split(r'[.!?]+', transcript)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        # Find key sentences based on important words
        key_words = [
            'decided', 'agreed', 'concluded', 'discussed', 'reviewed',
            'planned', 'proposed', 'announced', 'confirmed', 'established'
        ]
        
        key_sentences = []
        for sentence in sentences[:20]:  # Look at first 20 sentences
            sentence_lower = sentence.lower()
            if any(word in sentence_lower for word in key_words):
                key_sentences.append(sentence)
        
        # Create summary
        if key_sentences:
            summary = "The meeting covered the following key topics: " + ". ".join(key_sentences[:3])
            if len(summary) > 500:
                summary = summary[:500] + "..."
            return summary
        else:
            # Fallback summary
            words = transcript.split()
            if len(words) > 50:
                return f"Meeting discussion involving {len(self.extract_participants(transcript))} participants covering various topics including project updates, decisions, and action items."
            else:
                return "Brief meeting discussion recorded."
    
    def extract_key_points(self, transcript: str) -> List[str]:
        """Extract key discussion points"""
        # Split into sentences
        sentences = re.split(r'[.!?]+', transcript)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 15]
        
        # Keywords that indicate important points
        important_keywords = [
            'decided', 'agreed', 'concluded', 'important', 'critical', 'urgent',
            'deadline', 'budget', 'proposal', 'recommendation', 'issue', 'problem',
            'solution', 'strategy', 'plan', 'goal', 'objective', 'milestone',
            'revenue', 'client', 'project', 'timeline', 'approval'
        ]
        
        key_points = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in important_keywords):
                if len(sentence.split()) > 5:  # Filter out very short sentences
                    key_points.append(sentence.strip())
        
        return key_points[:5]  # Return top 5 key points
    
    def extract_action_items(self, transcript: str, participants: List[str]) -> List[ActionItem]:
        """Extract action items and assign tasks"""
        action_patterns = [
            r'([A-Z][a-z]+)\s+will\s+([^.!?]+)',  # "John will complete the report"
            r'([A-Z][a-z]+)\s+should\s+([^.!?]+)',  # "Sarah should review the budget"
            r'([A-Z][a-z]+)\s+needs to\s+([^.!?]+)',  # "Mike needs to call the client"
            r'([A-Z][a-z]+)\s+is responsible for\s+([^.!?]+)',  # "Alice is responsible for testing"
            r'([A-Z][a-z]+)\s+please\s+([^.!?]+)',  # "John please handle this"
        ]
        
        action_items = []
        
        for pattern in action_patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:  # assignee and task
                    assignee, task = match
                    if len(task.strip()) > 5:  # Valid task
                        action_items.append(ActionItem(
                            task=task.strip(),
                            assignee=assignee,
                            deadline=self._extract_deadline(task),
                            priority=self._determine_priority(task)
                        ))
        
        # Also look for general action items
        action_keywords = ['action item', 'todo', 'follow up', 'next step', 'assigned']
        sentences = re.split(r'[.!?]+', transcript)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in action_keywords):
                # Try to extract assignee
                assignee = "TBD"
                for participant in participants:
                    if participant.lower() in sentence_lower:
                        assignee = participant
                        break
                
                if len(sentence.strip()) > 10:
                    action_items.append(ActionItem(
                        task=sentence.strip(),
                        assignee=assignee,
                        deadline=self._extract_deadline(sentence),
                        priority=self._determine_priority(sentence)
                    ))
        
        return action_items[:8]  # Limit to 8 action items
    
    def _extract_deadline(self, task: str) -> str:
        """Extract deadline from task description"""
        deadline_patterns = [
            r'by\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
            r'by\s+(next\s+week|this\s+week)',
            r'by\s+(\d{1,2}/\d{1,2})',  # "by 12/25"
            r'within\s+(\d+)\s+days?',  # "within 3 days"
            r'by\s+(tomorrow|today)',
            r'end of\s+(week|month|day)',
        ]
        
        for pattern in deadline_patterns:
            match = re.search(pattern, task.lower())
            if match:
                return match.group(1)
        
        return "TBD"
    
    def _determine_priority(self, task: str) -> str:
        """Determine task priority based on keywords"""
        urgent_keywords = ['urgent', 'asap', 'immediately', 'critical', 'emergency', 'today', 'tomorrow']
        high_keywords = ['important', 'priority', 'deadline', 'client', 'board', 'approval']
        
        task_lower = task.lower()
        
        if any(keyword in task_lower for keyword in urgent_keywords):
            return "Urgent"
        elif any(keyword in task_lower for keyword in high_keywords):
            return "High"
        else:
            return "Medium"
    
    def process_meeting(self, transcript: str, meeting_title: str = "") -> MeetingSummary:
        """Process complete meeting transcript"""
        participants = self.extract_participants(transcript)
        summary = self.generate_summary(transcript)
        key_points = self.extract_key_points(transcript)
        action_items = self.extract_action_items(transcript, participants)
        
        return MeetingSummary(
            title=meeting_title or f"Meeting Summary - {datetime.now().strftime('%Y-%m-%d')}",
            date=datetime.now().strftime('%Y-%m-%d %H:%M'),
            participants=participants,
            summary=summary,
            key_points=key_points,
            action_items=action_items,
            next_meeting=self._extract_next_meeting(transcript)
        )
    
    def _extract_next_meeting(self, transcript: str) -> str:
        """Extract next meeting information"""
        next_meeting_patterns = [
            r'next meeting\s+([^.!?]+)',
            r'follow.up\s+([^.!?]+)',
            r'meet again\s+([^.!?]+)',
            r'schedule.*?meeting\s+([^.!?]+)',
        ]
        
        for pattern in next_meeting_patterns:
            match = re.search(pattern, transcript.lower())
            if match:
                return match.group(1).strip()
        
        return "TBD"

def main():
    """Main Streamlit application"""
    st.set_page_config(
        page_title="AI Meeting Summarizer",
        layout="wide"
    )
    
    st.title(" AI Meeting Summarizer")
    st.markdown("Transform your meeting transcripts into actionable insights")
    
    # Initialize summarizer
    if 'summarizer' not in st.session_state:
        st.session_state.summarizer = SimpleMeetingSummarizer()
    
    # Sidebar
    st.sidebar.header("Settings")
    meeting_title = st.sidebar.text_input("Meeting Title", "Weekly Project Review")
    
    # Sample transcripts
    sample_transcripts = {
        "Sales Meeting": """John: Good morning everyone. Let's start with the Q4 sales review.
Sarah: Our revenue is up 15% compared to last quarter. The new product launch was successful.
Mike: I need to follow up with three key clients by Friday. The enterprise deals are progressing well.
Sarah: We should prepare the quarterly report by next Tuesday. 
John: Great. Mike, please schedule client calls this week. Sarah will handle the report.
Lisa: The marketing campaign needs approval by tomorrow for the holiday push.
John: Lisa, get that approved ASAP. Next meeting is scheduled for next Monday at 10 AM.""",
        
        "Project Planning": """Alex: Let's discuss the new website redesign project timeline.
Emma: The design mockups are ready for review. We need client feedback by Wednesday.
Tom: I'll handle the backend development. Estimated completion is two weeks.
Emma: The user testing phase should start next Friday. Tom, can you have the staging environment ready?
Alex: Emma will coordinate with the client. Tom is responsible for development milestones.
Sam: We need to update the project documentation and notify stakeholders about the timeline.
Alex: Sam, please send updates to stakeholders by end of day. Critical that we meet the December deadline.""",
        
        "Budget Review": """Director: Our department budget for next year needs careful planning.
Manager1: The software licenses are increasing by 20%. We need to allocate more budget there.
Manager2: I recommend reducing travel expenses and focusing on virtual meetings.
Director: Good point. Manager1 will research alternative software solutions by next week.
Manager2: I'll prepare a cost analysis comparing virtual vs in-person events.
Director: Both reports are due before the board meeting on Friday. This is high priority.
Manager1: Should we also review the vendor contracts?
Director: Yes, Manager2 please audit all vendor agreements within the next two weeks."""
    }
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Meeting Transcript")
        
        # Sample selector
        selected_sample = st.selectbox("Load Sample Transcript:", [""] + list(sample_transcripts.keys()))
        if selected_sample:
            st.session_state.transcript = sample_transcripts[selected_sample]
        
        # Text input
        transcript = st.text_area(
            "Paste your meeting transcript here:",
            value=st.session_state.get('transcript', ''),
            height=300,
            placeholder="Enter the meeting transcript or select a sample above..."
        )
        
        if st.button(" Analyze Meeting", type="primary"):
            if transcript.strip():
                with st.spinner("Processing meeting transcript..."):
                    result = st.session_state.summarizer.process_meeting(transcript, meeting_title)
                    st.session_state.analysis_result = result
                st.success("Analysis complete!")
            else:
                st.error("Please enter a meeting transcript.")
    
    with col2:
        st.subheader("Quick Stats")
        if transcript:
            words = len(transcript.split())
            sentences = len(re.split(r'[.!?]+', transcript))
            
            st.metric("Word Count", words)
            st.metric("Sentences", sentences)
            st.metric("Estimated Reading Time", f"{words // 200 + 1} min")
    
    # Display results
    if 'analysis_result' in st.session_state:
        result = st.session_state.analysis_result
        
        st.divider()
        st.header("Meeting Analysis Results")
        
        # Summary section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📝 Meeting Summary")
            st.write(result.summary)
            
            if result.key_points:
                st.subheader("🎯 Key Discussion Points")
                for i, point in enumerate(result.key_points, 1):
                    st.write(f"{i}. {point}")
            else:
                st.info("No specific key points identified in this transcript.")
        
        with col2:
            st.subheader("👥 Participants")
            if result.participants:
                for participant in result.participants:
                    st.write(f"• {participant}")
            else:
                st.info("No participants identified")
            
            st.subheader(" Meeting Details")
            st.write(f"**Date:** {result.date}")
            st.write(f"**Next Meeting:** {result.next_meeting}")
        
        # Action items
        st.subheader("✅ Action Items & Task Assignments")
        
        if result.action_items:
            # Create a table for action items
            action_data = []
            for item in result.action_items:
                action_data.append({
                    "Task": item.task[:100] + "..." if len(item.task) > 100 else item.task,
                    "Assignee": item.assignee,
                    "Deadline": item.deadline,
                    "Priority": item.priority
                })
            
            st.dataframe(action_data, use_container_width=True)
            
            # Priority breakdown
            st.subheader(" Priority Breakdown")
            priority_counts = {}
            for item in result.action_items:
                priority_counts[item.priority] = priority_counts.get(item.priority, 0) + 1
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🔴 Urgent", priority_counts.get("Urgent", 0))
            with col2:
                st.metric("🟡 High", priority_counts.get("High", 0))
            with col3:
                st.metric("🟢 Medium", priority_counts.get("Medium", 0))
        else:
            st.info("No specific action items detected in this meeting.")
        
        # Export functionality
        st.subheader(" Export Options")
        
        # Create exportable summary
        export_text = f"""MEETING SUMMARY
===============
Title: {result.title}
Date: {result.date}
Participants: {', '.join(result.participants) if result.participants else 'Not identified'}

SUMMARY
-------
{result.summary}

KEY POINTS
----------
{chr(10).join([f"• {point}" for point in result.key_points]) if result.key_points else 'No key points identified'}

ACTION ITEMS
------------
{chr(10).join([f"• [{item.priority}] {item.task} (Assigned: {item.assignee}, Due: {item.deadline})" for item in result.action_items]) if result.action_items else 'No action items identified'}

NEXT MEETING
------------
{result.next_meeting}
"""
        
        st.download_button(
            label="Download Summary (TXT)",
            data=export_text,
            file_name=f"meeting_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )
        
        # JSON export
        json_data = {
            "title": result.title,
            "date": result.date,
            "participants": result.participants,
            "summary": result.summary,
            "key_points": result.key_points,
            "action_items": [
                {
                    "task": item.task,
                    "assignee": item.assignee,
                    "deadline": item.deadline,
                    "priority": item.priority
                } for item in result.action_items
            ],
            "next_meeting": result.next_meeting
        }
        
        st.download_button(
            label=" Download Data (JSON)",
            data=json.dumps(json_data, indent=2),
            file_name=f"meeting_data_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json"
        )

if __name__ == "__main__":
    main()