/****** Object:  Table [dbo].[DimCurrency]    Script Date: 12/11/2025 5:45:34 pm ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[DimCurrency](
	[CurrencyKey] [int] IDENTITY(1,1) NOT NULL,
	[CurrencyCode] [nchar](10) NOT NULL,
	[SiteCode] [nchar](10) NOT NULL,
	[CurrencyName] [nvarchar](50) NOT NULL,
	[CurrencySymbol] [nvarchar](10) NOT NULL,
 CONSTRAINT [PK_DimCurrency_CurrencyKey] PRIMARY KEY CLUSTERED 
(
	[CurrencyKey] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO


