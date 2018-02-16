# SIP Science Pipeline Workflows

## Description
This package contains a set of Science Pipeline Workflows scripts or 
applications.

Science Pipeline Workflows are data driven workflows, expressed in a terms of 
an Execution Framework API and make use of Core Processing functions or 
Processing Wrappers provided by the Execution Framework implementation.

Science Pipeline workflows will be executed by the Workflow Engine 
(in the Processing Block Controller) using an Execution Framework runtime, the
interface to which is expected to be abstracted away using the execution
framework interface library.

The expected steps necessary to execute a data-driven workflow, will typically 
involve:

1. Configuring the buffer to provide required Data Islands
2. Creating Data queues for dynamic data
3. Initialising Quality Assessment to generate appropriate metrics
4. Using Model Database to extract a Science Data Model
5. Employing Execution Framework instances to execute workflows on available 
   processing resources.
6. Update the Science Data Product Catalogue in the Data Preparation and 
   Delivery

The scripts or applications defined in this package will mainly be concerned 
with step 5 in the above description.

Note: In the SIP code we expect to have a small number of example 
demonstration pipeline workflows in this package whose main role is to 
provide a platform for exercising interfaces with services in the SIP SDP 
software stack.
