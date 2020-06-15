resource "aws_subnet" "public_subnet" {
  vpc_id = aws_vpc.base_vpc.id
  cidr_block = cidrsubnet(aws_vpc.base_vpc.cidr_block,3,4)

  tags = merge(local.default_tags, {
    Name = "${local.resource_prefix}-public_subnet"
  })
}