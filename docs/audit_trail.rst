Audit trail
###########


Phase features an audit trail, i.e activity stream logging users actions.  
The audit trail is loosely based on Activity Stream specification http://activitystrea.ms/specs/json/1.0/

We log:

* The actor:  the object that performed the activity (user or system)
* The verb of the action
* The action object : the object linked to the action itself
* The target: the object to which the activity was performed
* The action timestamp

Action object and target are optional
Action object, Actor and target are also denormalized in a Charfield to keep the record even
if related objects are deleted.

Actions logged
--------------

Currently, actions logged are defined in audit_trail.models.Activity::  

    VERB_CREATED = 'created'
    VERB_EDITED = 'edited'
    VERB_DELETED = 'deleted'
    VERB_JOINED = 'joined'
    VERB_STARTED_REVIEW = 'started_review'
    VERB_CANCELLED_REVIEW = 'cancelled_review'
    VERB_REVIEWED = 'reviewed'
    VERB_CLOSED_REVIEWER_STEP = 'closed_reviewer_step'
    VERB_CLOSED_LEADER_STEP = 'closed_leader_step'
    VERB_CLOSED_APPROVER_STEP = 'closed_approver_step'
    VERB_SENT_BACK_TO_LEADER_STEP = 'sent_back_to_leader_step'

A signal is defined in audit_trail.signals and sent in relevant part of the application.

For admins
----------

The audit trail displaying all users activities is accessible in django admin interface for
admin users.

For other users
---------------

User having `documents.can_control_document` permission can access the document audit trail by the action dropdown menu.

