#!/usr/bin/env node
import "source-map-support/register";
import * as cdk from "aws-cdk-lib";
import { HealthflowStack } from "../lib/healthflow-stack";

const app = new cdk.App();
const account = process.env.CDK_DEFAULT_ACCOUNT ?? "000000000000";
const region = process.env.CDK_DEFAULT_REGION ?? "us-east-1";

new HealthflowStack(app, "HealthflowStack", {
  env: { account, region }
});
