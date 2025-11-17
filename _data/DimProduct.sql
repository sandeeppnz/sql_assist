/****** Object:  Table [dbo].[DimProduct]    Script Date: 12/11/2025 5:48:45 pm ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[DimProduct](
	[ProductKey] [int] IDENTITY(1,1) NOT NULL,
	[ProductCode] [nvarchar](36) NOT NULL,
	[Brand] [nvarchar](36) NULL,
	[Description] [nvarchar](255) NULL,
	[PackSize] [nvarchar](30) NULL,
	[InventoryGroup] [nvarchar](20) NULL,
	[ProductSaleCategoryCode] [nvarchar](36) NULL,
	[ProductSaleCategoryDescription] [nvarchar](100) NULL,
	[ProductLineCode] [nvarchar](36) NULL,
	[ProductLineDescription] [nvarchar](100) NULL,
	[SubClassCode] [nvarchar](50) NULL,
	[SubClassDescription] [nvarchar](400) NULL,
	[InvUOMCode] [nvarchar](10) NULL,
	[InvUOMDescription] [nvarchar](50) NULL,
	[OuterUOMCode] [nvarchar](10) NULL,
	[OuterUOMDescription] [nvarchar](50) NULL,
	[AlternateUOMCode] [nvarchar](10) NULL,
	[AlternateUOMDescription] [nvarchar](50) NULL,
	[CatalogueItem] [nchar](1) NULL,
	[PubliclyAvailable] [nchar](1) NULL,
	[TaxRate] [decimal](18, 2) NULL,
	[OuterPackSize] [nvarchar](20) NULL,
	[Status] [nvarchar](36) NULL,
	[StatusShortName] [nvarchar](2) NULL,
	[_SourceSiteCode] [nvarchar](3) NOT NULL,
	[_SourceItemCode] [nvarchar](36) NOT NULL,
	[_SourceProductCode] [nvarchar](36) NOT NULL,
	[ValidFrom] [datetime2](7) NULL,
	[ValidTo] [datetime2](7) NULL,
	[LastLoadedDateTime] [datetime] NOT NULL,
 CONSTRAINT [PK_DimProduct] PRIMARY KEY CLUSTERED 
(
	[ProductKey] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO


