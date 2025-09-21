# ────────────────
# API Gateway REST API root
# ────────────────
resource "aws_api_gateway_rest_api" "api" {
  name        = "content-api"
  description = "API Gateway for content processing app"
}

# ────────────────
# /new_post resource + POST
# ────────────────
resource "aws_api_gateway_resource" "new_post" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "new_post"
}

resource "aws_api_gateway_method" "new_post_post" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.new_post.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "new_post_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.new_post.id
  http_method             = aws_api_gateway_method.new_post_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.new_post.invoke_arn
}

# CORS: OPTIONS for /new_post
resource "aws_api_gateway_method" "new_post_options" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.new_post.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "new_post_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.new_post.id
  http_method = aws_api_gateway_method.new_post_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "new_post_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.new_post.id
  http_method = aws_api_gateway_method.new_post_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"  = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Headers" = true
  }
}

resource "aws_api_gateway_integration_response" "new_post_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.new_post.id
  http_method = aws_api_gateway_method.new_post_options.http_method
  status_code = aws_api_gateway_method_response.new_post_options.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
    "method.response.header.Access-Control-Allow-Methods" = "'OPTIONS,POST'"
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
  }
}

# ────────────────
# /get-post resource + GET
# ────────────────
resource "aws_api_gateway_resource" "get_post" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  path_part   = "get-post"
}

resource "aws_api_gateway_method" "get_post_get" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.get_post.id
  http_method   = "GET"
  authorization = "NONE"

  request_parameters = {
    "method.request.querystring.postId" = false
  }
}

resource "aws_api_gateway_integration" "get_post_integration" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.get_post.id
  http_method             = aws_api_gateway_method.get_post_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.get_post.invoke_arn
}

# CORS: OPTIONS for /get-post
resource "aws_api_gateway_method" "get_post_options" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.get_post.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "get_post_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.get_post.id
  http_method = aws_api_gateway_method.get_post_options.http_method
  type        = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "get_post_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.get_post.id
  http_method = aws_api_gateway_method.get_post_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"  = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Headers" = true
  }
}

resource "aws_api_gateway_integration_response" "get_post_options" {
  rest_api_id = aws_api_gateway_rest_api.api.id
  resource_id = aws_api_gateway_resource.get_post.id
  http_method = aws_api_gateway_method.get_post_options.http_method
  status_code = aws_api_gateway_method_response.get_post_options.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
    "method.response.header.Access-Control-Allow-Methods" = "'OPTIONS,GET'"
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
  }
}

# ────────────────
# Lambda Permissions
# ────────────────
resource "aws_lambda_permission" "apigw_invoke_new_post" {
  statement_id  = "AllowAPIGatewayInvokeNewPost"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.new_post.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "apigw_invoke_get_post" {
  statement_id  = "AllowAPIGatewayInvokeGetPost"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.get_post.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "apigw_invoke_convert_to_audio" {
  statement_id  = "AllowAPIGatewayInvokeConvertToAudio"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.convert_to_audio.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
}

# ────────────────
# Deployment
# ────────────────
resource "aws_api_gateway_deployment" "deployment" {
  depends_on = [
    aws_api_gateway_integration.new_post_integration,
    aws_api_gateway_integration.get_post_integration,
    aws_api_gateway_integration_response.new_post_options,
    aws_api_gateway_integration_response.get_post_options
  ]
  rest_api_id = aws_api_gateway_rest_api.api.id

  triggers = {
    redeploy = "${filebase64sha256("../deploy/handler.zip")}-${filebase64sha256("../deploy/convert_to_audio.zip")}-${filebase64sha256("../deploy/get_post.zip")}"
  }
}

resource "aws_api_gateway_stage" "prod" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  stage_name    = "prod"
  deployment_id = aws_api_gateway_deployment.deployment.id
}