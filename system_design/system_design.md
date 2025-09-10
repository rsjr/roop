# Part 2 - System Design

Second part of Entail's challenge.

## How would you handle long-running WoW analyses (typ > 10 seconds)?

I would explore the approach of having a async queue + worker architecture, splitting what (in my PoC) is running all together three main components:

* API Layer: just the Fast API routes + the service part needed for CRUD (tasks and schedules) - PRODUCER
* "Common" layer: shared Pydantic schemas, constants, enums etc etc.
* Worker layer: calculation worker, which will do the heavy lifting (fetching from weather API + doing the calculations needed) - CONSUMER

The async queue (probably with a persistence layer) will orchestrate the API module and the worker module in a producer/consumer approach.

ADD DIAGRAM HERE HERE

This architecture has the following advantages:
* Remove the single point of failure, as API and worker will be deployed in different container (pods)
* You can have more control on rate limiting by monitoring the amount of in process (in flight) requests between producer and consumer
* Flexiblity when scaling (heavy usage on worker side vs heavy usage on API side vs both)
* In a scenario where you are depending on a external system (such as a weather API), you dettach the inflight requests coming to the API to our calls to the external service. In a nutshell: you don't keep the user "hanging" because the service is stuck in I/O to an external third party system
* Full async between frotnend and worker. The API will give the end user a requestId, and the user is responsible for polling the API until the result is done. This makes the experience fluid in the frontend without long waiting times.
* You can even implement a batch worker, scheduled based. 

## How would you implement notifications, e.g. notify relevant users when a task is completed?
We might need to introduce an event based architecturem depending on constraints, but I would probably rely on AWS SNS for this. Kafka or other more robust solutions are also valid, but I would use cloud resources which are already proven to work nicely (obviosly, taking into account the cost of using "out-of-the-box" solutions)

## How would you ensure **scalability** if hundreds of vessels query forecasts concurrently?

Despite the approach taken, the deployment probably will be hosted in a Kubernetes cluster, where KEDA is in place.
KEDA is a powerful tool to automate scalability an a elastic way and configurable way. Or, something like EKS can also be used, but then you are tied to a Cloud provider (such AWS in this case.)

## How would you ensure **high availability and fault tolerance** in a cloud environment?

This area will be the one where I would need to study and develop more myself, but to be very honest, I would use as much as tools possible from the cloud provider.

In terms of HA, AWS has a set of tools in order to keep database redundancy, backups (hot/cold), regional availability etc. This probably is/will be a key factor when deciding which database to use and how to host it (AWS RDS has different tools when compared to Aurora, for example).


## How would you secure access to the APIs (authentication, rate-limiting, etc.)?
I will rely on industry standands for this. As much as battle-tested, the better.

### Authentication
OAuth (JWT) + Cloud provider IdP for user session / authentication and role based setup. (Azure Entra ID, AWS IdP etc)
Unless some specific requirements come into place, I would use the most standard and tested setup as possible here.

### Rate limiting
This is for me one of the key parts of a scalable service: Defining limits. It's something to be taken into consideration in the early phase of design/development, as this will be the north star for usage, consumption and overall costs. If limits are well set and the users know how to expect, you can have a stable service and save money, plain and simple.

Only sending 429s when throttling is a start, but in my opinion, is a bit beyond that. When designing a service, you need to fully understand what is the expected load and how to scale if it gets bigger. The limits are the guardrails that will allow to do that without outages. Also, have clear and proper documentation in place so the end users understand their limits and the behavior when the limits are reached.