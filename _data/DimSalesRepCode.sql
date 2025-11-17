/****** Object:  Table [dbo].[DimSalesRepCode]    Script Date: 12/11/2025 5:49:00 pm ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[DimSalesRepCode](
	[SalesRepCodeKey] [int] IDENTITY(1,1) NOT NULL,
	[SalesRepCode] [nvarchar](36) NULL,
	[_SourceSiteCode] [nvarchar](2) NULL,
	[ValidFrom] [datetime2](7) NULL,
	[ValidTo] [datetime2](7) NULL,
	[LastLoadedDateTime] [datetime2](7) NULL,
 CONSTRAINT [PK_DimSalesRepCode] PRIMARY KEY CLUSTERED 
(
	[SalesRepCodeKey] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO


