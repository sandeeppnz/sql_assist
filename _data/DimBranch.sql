/****** Object:  Table [dbo].[DimBranch]    Script Date: 12/11/2025 5:44:11 pm ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[DimBranch](
	[BranchKey] [int] IDENTITY(1,1) NOT NULL,
	[CurrencyKey] [int] NOT NULL,
	[GeographyKey] [int] NOT NULL,
	[BranchCode] [nvarchar](36) NOT NULL,
	[BranchName] [nvarchar](150) NOT NULL,
	[_SourceBranchKey] [int] NULL,
	[_SourceSiteCode] [nvarchar](2) NULL,
	[ValidFrom] [datetime] NULL,
	[ValidTo] [datetime] NULL,
	[LastLoadedDateTime] [datetime] NULL,
 CONSTRAINT [PK_Branches] PRIMARY KEY CLUSTERED 
(
	[BranchKey] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[DimBranch]  WITH CHECK ADD  CONSTRAINT [FK_DimBranch_DimCurrency] FOREIGN KEY([CurrencyKey])
REFERENCES [dbo].[DimCurrency] ([CurrencyKey])
GO

ALTER TABLE [dbo].[DimBranch] CHECK CONSTRAINT [FK_DimBranch_DimCurrency]
GO

ALTER TABLE [dbo].[DimBranch]  WITH CHECK ADD  CONSTRAINT [FK_DimBranch_DimGeography] FOREIGN KEY([GeographyKey])
REFERENCES [dbo].[DimGeography] ([GeographyKey])
GO

ALTER TABLE [dbo].[DimBranch] CHECK CONSTRAINT [FK_DimBranch_DimGeography]
GO


