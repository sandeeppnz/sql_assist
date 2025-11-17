/****** Object:  Table [dbo].[DimCustomer]    Script Date: 12/11/2025 5:46:09 pm ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[DimCustomer](
	[CustomerKey] [int] IDENTITY(1,1) NOT NULL,
	[WarehouseKey] [int] NOT NULL,
	[ParentCustomerKey] [int] NULL,
	[ChildCustomerKey] [int] NULL,
	[AccountCode] [nvarchar](36) NOT NULL,
	[AccountName] [nvarchar](100) NOT NULL,
	[AccountType] [nvarchar](20) NOT NULL,
	[AccountTypeShortName] [nvarchar](2) NOT NULL,
	[MemberSince] [datetime2](7) NULL,
	[CustomerAgeInDays] [int] NULL,
	[EightWeeksBusinessPotential] [money] NULL,
	[Status] [nvarchar](20) NOT NULL,
	[StatusShortName] [nvarchar](2) NOT NULL,
	[ReportingGroup] [nvarchar](50) NULL,
	[PricingGroupCode] [nvarchar](36) NULL,
	[PricingGroup] [nvarchar](36) NULL,
	[IndustryGroupCode] [nvarchar](36) NULL,
	[IndustryGroupName] [nvarchar](100) NULL,
	[SalesRepresentativeCode] [nvarchar](100) NULL,
	[RunNumber] [nvarchar](36) NULL,
	[RunSequenceNumber] [nvarchar](36) NULL,
	[ZeroRateSalesTax] [nchar](1) NULL,
	[ParentAccountCode] [nvarchar](36) NULL,
	[ChildAccountCode] [nvarchar](36) NULL,
	[_SourceAccountCode] [nvarchar](36) NULL,
	[_SourceCustomerKey] [int] NULL,
	[_SourceSiteCode] [nvarchar](3) NULL,
	[ValidFrom] [datetime2](7) NULL,
	[ValidTo] [datetime2](7) NULL,
	[LastLoadedDateTime] [datetime] NOT NULL,
 CONSTRAINT [PK_DimCustomer] PRIMARY KEY CLUSTERED 
(
	[CustomerKey] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[DimCustomer]  WITH CHECK ADD  CONSTRAINT [FK_DimCustomer_DimWarehouse_WarehouseKey] FOREIGN KEY([WarehouseKey])
REFERENCES [dbo].[DimWarehouse] ([WarehouseKey])
GO

ALTER TABLE [dbo].[DimCustomer] CHECK CONSTRAINT [FK_DimCustomer_DimWarehouse_WarehouseKey]
GO


