# Code Jam – Judge Backend
This repository contains the **judge-facing backend service** for our Code Jam project.

## Purpose
The judge backend is responsible for:
- Receiving submissions from teams
- Scoring submissions based on Code Jam rules
- Tracking timestamps and attempt counts
- Returning feedback for incorrect submissions
- Providing data for the scoreboard

## Tech Stack
- Language: Python
- Framework: Flask
- Database: TBD (initial demo uses in-memory data)

## Status
- Initial architecture and API design in progress  
- Scoring logic defined  
- API endpoints being stubbed for customer demo

## Team Coordination
This service exposes a consolidated set of API endpoints used by:
- Team-side submission system
- Security layer
- Scoreboard / design frontend

API contracts are being finalized to ensure consistency across teams.
