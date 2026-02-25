import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as apigw from "aws-cdk-lib/aws-apigateway";
import * as dynamodb from "aws-cdk-lib/aws-dynamodb";
import * as events from "aws-cdk-lib/aws-events";
import * as targets from "aws-cdk-lib/aws-events-targets";
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as lambdaEventSources from "aws-cdk-lib/aws-lambda-event-sources";
import * as sqs from "aws-cdk-lib/aws-sqs";
import * as path from "path";

export class HealthflowStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const localstackEndpoint = process.env.LOCALSTACK_ENDPOINT ?? "";

    const eventBus = new events.EventBus(this, "HealthflowBus", {
      eventBusName: "healthflow-bus"
    });

    const eventsTable = new dynamodb.Table(this, "EventsTable", {
      tableName: "healthflow-events",
      partitionKey: { name: "event_id", type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY
    });

    const usersTable = new dynamodb.Table(this, "UsersTable", {
      tableName: "healthflow-users",
      partitionKey: { name: "username", type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY
    });

    const patientsTable = new dynamodb.Table(this, "PatientsTable", {
      tableName: "healthflow-patients",
      partitionKey: { name: "patient_id", type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY
    });

    const observationsTable = new dynamodb.Table(this, "ObservationsTable", {
      tableName: "healthflow-observations",
      partitionKey: { name: "observation_id", type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY
    });

    const alertsTable = new dynamodb.Table(this, "AlertsTable", {
      tableName: "healthflow-alerts",
      partitionKey: { name: "alert_id", type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY
    });

    const queue = new sqs.Queue(this, "ObservationQueue", {
      queueName: "healthflow-observation-queue",
      visibilityTimeout: cdk.Duration.seconds(30)
    });

    const lambdaCode = lambda.Code.fromAsset(path.join(__dirname, "../../services"));

    const baseEnv: Record<string, string> = {
      EVENT_BUS_NAME: eventBus.eventBusName,
      EVENTS_TABLE: eventsTable.tableName,
      USERS_TABLE: usersTable.tableName,
      PATIENTS_TABLE: patientsTable.tableName,
      OBSERVATIONS_TABLE: observationsTable.tableName,
      ALERTS_TABLE: alertsTable.tableName,
      ALERT_THRESHOLD: "7",
      JWT_SECRET: "dev-secret"
    };

    if (localstackEndpoint) {
      baseEnv.AWS_ENDPOINT_URL = localstackEndpoint;
    }

    const authLambda = new lambda.Function(this, "AuthLambda", {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: "auth.handler.lambda_handler",
      code: lambdaCode,
      environment: baseEnv,
      timeout: cdk.Duration.seconds(10)
    });

    const authorizerLambda = new lambda.Function(this, "AuthorizerLambda", {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: "authorizer.handler.lambda_handler",
      code: lambdaCode,
      environment: baseEnv,
      timeout: cdk.Duration.seconds(10)
    });

    const patientCommand = new lambda.Function(this, "PatientCommandLambda", {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: "patient_command.handler.lambda_handler",
      code: lambdaCode,
      environment: baseEnv,
      timeout: cdk.Duration.seconds(10)
    });

    const observationCommand = new lambda.Function(this, "ObservationCommandLambda", {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: "observation_command.handler.lambda_handler",
      code: lambdaCode,
      environment: baseEnv,
      timeout: cdk.Duration.seconds(10)
    });

    const queryAlerts = new lambda.Function(this, "QueryAlertsLambda", {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: "query_alerts.handler.lambda_handler",
      code: lambdaCode,
      environment: baseEnv,
      timeout: cdk.Duration.seconds(10)
    });

    const projectionPatient = new lambda.Function(this, "ProjectionPatientLambda", {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: "projection_patient.handler.lambda_handler",
      code: lambdaCode,
      environment: baseEnv,
      timeout: cdk.Duration.seconds(10)
    });

    const projectionObservation = new lambda.Function(this, "ProjectionObservationLambda", {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: "projection_observation.handler.lambda_handler",
      code: lambdaCode,
      environment: baseEnv,
      timeout: cdk.Duration.seconds(10)
    });

    const projectionAlert = new lambda.Function(this, "ProjectionAlertLambda", {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: "projection_alert.handler.lambda_handler",
      code: lambdaCode,
      environment: baseEnv,
      timeout: cdk.Duration.seconds(10)
    });

    const alertWorker = new lambda.Function(this, "AlertWorkerLambda", {
      runtime: lambda.Runtime.PYTHON_3_11,
      handler: "alert_worker.handler.lambda_handler",
      code: lambdaCode,
      environment: baseEnv,
      timeout: cdk.Duration.seconds(10)
    });

    alertWorker.addEventSource(new lambdaEventSources.SqsEventSource(queue, { batchSize: 5 }));

    eventsTable.grantWriteData(authLambda);
    usersTable.grantReadWriteData(authLambda);
    eventBus.grantPutEventsTo(authLambda);

    eventsTable.grantWriteData(patientCommand);
    eventBus.grantPutEventsTo(patientCommand);

    eventsTable.grantWriteData(observationCommand);
    eventBus.grantPutEventsTo(observationCommand);

    eventsTable.grantWriteData(alertWorker);
    eventBus.grantPutEventsTo(alertWorker);

    patientsTable.grantWriteData(projectionPatient);
    observationsTable.grantWriteData(projectionObservation);
    alertsTable.grantWriteData(projectionAlert);

    alertsTable.grantReadData(queryAlerts);

    usersTable.grantReadData(queryAlerts);
    patientsTable.grantReadData(queryAlerts);

    const api = new apigw.RestApi(this, "HealthflowApi", {
      restApiName: "healthflow-api",
      deployOptions: { stageName: "local" },
      defaultCorsPreflightOptions: {
        allowOrigins: apigw.Cors.ALL_ORIGINS,
        allowMethods: apigw.Cors.ALL_METHODS,
        allowHeaders: apigw.Cors.DEFAULT_HEADERS
      }
    });

    const login = api.root.addResource("login");
    login.addMethod("POST", new apigw.LambdaIntegration(authLambda));

    const useAuthorizer = !localstackEndpoint;
    const authOptions = useAuthorizer
      ? {
          authorizer: new apigw.TokenAuthorizer(this, "HealthflowAuthorizer", {
            handler: authorizerLambda
          }),
          authorizationType: apigw.AuthorizationType.CUSTOM
        }
      : undefined;

    const patients = api.root.addResource("patients");
    patients.addMethod("POST", new apigw.LambdaIntegration(patientCommand), authOptions);

    const observations = api.root.addResource("observations");
    observations.addMethod("POST", new apigw.LambdaIntegration(observationCommand), authOptions);

    const alerts = api.root.addResource("alerts");
    alerts.addMethod("GET", new apigw.LambdaIntegration(queryAlerts), authOptions);

    new events.Rule(this, "PatientCreatedRule", {
      eventBus,
      eventPattern: { detailType: ["PatientCreated"] },
      targets: [new targets.LambdaFunction(projectionPatient)]
    });

    new events.Rule(this, "ObservationProjectionRule", {
      eventBus,
      eventPattern: { detailType: ["ObservationSubmitted"] },
      targets: [new targets.LambdaFunction(projectionObservation)]
    });

    new events.Rule(this, "ObservationQueueRule", {
      eventBus,
      eventPattern: { detailType: ["ObservationSubmitted"] },
      targets: [new targets.SqsQueue(queue)]
    });

    new events.Rule(this, "AlertCreatedRule", {
      eventBus,
      eventPattern: { detailType: ["AlertCreated"] },
      targets: [new targets.LambdaFunction(projectionAlert)]
    });

    new cdk.CfnOutput(this, "ApiName", { value: api.restApiName });
  }
}
