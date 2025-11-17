/****** Object:  Table [dbo].[DimGeography]    Script Date: 12/11/2025 5:47:51 pm ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[DimGeography](
	[GeographyKey] [int] IDENTITY(1,1) NOT NULL,
	[SiteKey] [int] NOT NULL,
	[City] [nvarchar](30) NULL,
	[StateProvinceCode] [nvarchar](10) NULL,
	[StateProvinceName] [nvarchar](50) NULL,
	[CountryCode] [nvarchar](10) NULL,
	[CountryName] [nvarchar](50) NULL,
	[PostalCode] [nvarchar](15) NULL,
 CONSTRAINT [PK_DimGeography_GeographyKey] PRIMARY KEY CLUSTERED 
(
	[GeographyKey] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[DimGeography]  WITH CHECK ADD  CONSTRAINT [FK_DimGeography_DimSites] FOREIGN KEY([SiteKey])
REFERENCES [dbo].[DimSite] ([SiteKey])
GO

ALTER TABLE [dbo].[DimGeography] CHECK CONSTRAINT [FK_DimGeography_DimSites]
GO


