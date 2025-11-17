/****** Object:  Table [dbo].[DimSite]    Script Date: 12/11/2025 5:49:40 pm ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[DimSite](
	[SiteKey] [int] IDENTITY(1,1) NOT NULL,
	[SiteCode] [nvarchar](10) NOT NULL,
	[SiteName] [nvarchar](50) NOT NULL,
	[SiteGroup] [nvarchar](50) NULL,
	[TimeZone] [nvarchar](100) NULL,
 CONSTRAINT [PK_DimSalesTerritory_SalesTerritoryKey] PRIMARY KEY CLUSTERED 
(
	[SiteKey] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO


