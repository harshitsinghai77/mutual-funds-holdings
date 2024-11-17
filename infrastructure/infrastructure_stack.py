from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb_,
    aws_apigatewayv2 as _apigw
)
from constructs import Construct
from aws_cdk.aws_apigatewayv2_integrations import HttpLambdaIntegration

class LambdaAPIMutualFundsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # example resource
        base_lambda = _lambda.Function(self, 'MutualFundHoldingsAppLambda',
                                       handler='lambda-handler.handler',
                                       runtime=_lambda.Runtime.PYTHON_3_13,
                                       code=_lambda.Code.from_asset('lambda1'),
                                    #    code=_lambda.Code.from_asset('lambda_deployment_package.zip'),
                                       memory_size=128,
                                       timeout=Duration.seconds(30)
                                    )
        
        base_api = _apigw.HttpApi(self, 'MutualFundHoldingsAppAPIGateway', 
                                  api_name='MutualFundHoldingsAppAPI',
                                  cors_preflight=_apigw.CorsPreflightOptions(
                                      allow_origins=["https://mutual-fund-holdings.netlify.app"],  # Allowed origin
                                      allow_methods=[_apigw.CorsHttpMethod.GET, _apigw.CorsHttpMethod.POST],  # Allowed HTTP methods using CorsHttpMethod enum
                                      allow_headers=["*"],  # Allowed headers
                                  ))
        base_api_integration = HttpLambdaIntegration("MutualFundsAPILambdaIntegration", base_lambda)
        base_api.add_routes(
            path="/mutualfunds",
            methods=[_apigw.HttpMethod.GET],
            integration=base_api_integration,
        )
        base_api.add_routes(
            path="/compare-mutual-funds",
            methods=[_apigw.HttpMethod.POST],
            integration=base_api_integration,
        )

        # Create DynamoDb Table
        mutual_funds_table = dynamodb_.Table.from_table_name(self, "MutualFundsTableLogicalID", table_name='mutual_funds')
        mutual_funds_holdings_table = dynamodb_.Table.from_table_name(self, "MutualFundsHoldingsTableLogicalID", table_name='mutual_fund_holdings')
        # mutual_funds_table = dynamodb_.Table(
        #     self,
        #     'mutual_funds',
        #     table_name='mutual_funds',  # Set custom table name
        #     partition_key=dynamodb_.Attribute(
        #         name="mutual_fund_id", type=dynamodb_.AttributeType.STRING
        #     ),
        #     billing_mode=dynamodb_.BillingMode('PAY_PER_REQUEST'),
        #     table_class=dynamodb_.TableClass.STANDARD
        # )

        # mutual_funds_holdings_table = dynamodb_.Table(
        #     self,
        #     'mutual_fund_holdings',
        #     table_name='mutual_fund_holdings',  # Set custom table name
        #     partition_key=dynamodb_.Attribute(
        #         name="mutual_fund_id", type=dynamodb_.AttributeType.STRING
        #     ),
        #     billing_mode=dynamodb_.BillingMode('PAY_PER_REQUEST'),
        #     table_class=dynamodb_.TableClass.STANDARD
        # )

        mutual_funds_table.grant_read_write_data(base_lambda)
        mutual_funds_holdings_table.grant_read_write_data(base_lambda)
