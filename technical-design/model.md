## Technical overview

```plantuml

@startuml C4_Elements
!include <C4/C4_context>
!include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Container.puml

Person(user, "User", "Tracks workouts, nutrition, and recovery, and engages socially through posts, chats, and groups.")

System_Boundary(strava1, "Strava+1 Platform") {

    Container(mobileApp, "Mobile Application", "iOS (Swift) & Android (Kotlin)", "Offers a native mobile experience for fitness tracking, chatting, notifications, and sharing progress on the go.")

    Container(backendApi, "Backend API", "FastAPI", "Handles business logic for workouts, nutrition, recovery, posts, comments, friendships, and notifications. Serves data to clients via REST API.")

    Container(realtimeService, "Real-Time Service", "FastAPI + WebSockets", "Handles live chat messages, live workout data, and notifications. Uses WebSockets to push events to connected mobile clients in real time.")

    Container(analyticsService, "Analytics Service", "AWS Lambda (Python)", "Processes workout, nutrition, and recovery data to generate insights, summaries, and progress metrics for users.")

    ContainerDb(globalDb, "Database", "PostgreSQL", "Stores user information, workout, nutrition, sleep, chat messages, timestamps, and metadata.")
}

System_Ext(deviceIntegration, "Device Health APIs (Apple Health / Google Fit)", "Optional read-only synchronization of sleep and workout data.")
System_Ext(firebaseAuth, "Firebase Authentication", "Manages user authentication via Google, Apple, or Email/Password, and provides verified ID tokens.")
System_Ext(pushNotification, "Push Notification Service", "Delivers mobile push notifications to devices")
System_Ext(mediaStorage, "Amazon S3", "Stores and serves user-uploaded media files such as images and videos.")
System_Ext(mediaProcessor, "Amazon Media Processor (MediaConvert)", "Processes uploaded videos (transcoding, compression, and thumbnail generation).")

' User interactions
Rel(user, mobileApp, "Uses mobile app")

' Mobile App communication
Rel(mobileApp, backendApi, "Sends requests for standard data (workouts, posts, profile, synced health and workout data) also send new chat messages", "HTTPS/REST")
Rel(mobileApp, realtimeService, "Maintains WebSocket connection for chat messages and live workout notifications", "WebSocket")
Rel(mobileApp, firebaseAuth, "Authenticates via Firebase SDK (Google, Apple, Email)", "HTTPS")
Rel(mobileApp, deviceIntegration, "Reads workout and health metrics via platform APIs", "Native API (HealthKit / Google Fit)")
Rel(pushNotification, mobileApp, "Delivers push notifications to devices", "FCM / APNs")
Rel(mobileApp, mediaStorage, "Uploads/downloads media files via pre-signed URLs", "HTTPS")

' Backend interactions
Rel(backendApi, realtimeService, "Publishes live events like chat messages and notifications", "HTTPS")
Rel(backendApi, firebaseAuth, "Verifies Firebase ID tokens for authorized requests", "HTTPS")
Rel(backendApi, pushNotification, "Sends push notification requests (hydration reminders, feed updates, alerts) and new messages", "HTTPS")
Rel(backendApi, globalDb, "Reads/writes user data, workout, nutrition, sleep and chat messages", "PostgreSQL wire")
Rel(backendApi, mediaStorage, "Generates and manages pre-signed URLs for media access", "HTTPS (AWS SDK)")
Rel(backendApi, mediaProcessor, "Triggers video transcoding and processing jobs when new media is uploaded", "HTTPS (AWS SDK)")
Rel(mediaProcessor, mediaStorage, "Stores processed media outputs (optimized videos, thumbnails)", "S3 internal API")
Rel(mediaStorage, backendApi, "Emits upload event for processing trigger", "S3 Event Trigger")

' Analytics relationships
Rel(backendApi, analyticsService, "Triggers data processing jobs and retrieves generated insights", "HTTPS (AWS SDK)")
Rel(analyticsService, globalDb, "Reads user activity, workout, nutrition, and sleep data for analysis", "PostgreSQL wire")
Rel(analyticsService, backendApi, "Sends computed insights and metrics", "HTTPS")

@enduml
```
