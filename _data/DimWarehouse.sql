/****** Object:  Table [dbo].[DimWarehouse]    Script Date: 12/11/2025 5:50:12 pm ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[DimWarehouse](
	[WarehouseKey] [int] IDENTITY(1,1) NOT NULL,
	[BranchKey] [int] NOT NULL,
	[WarehouseCode] [nvarchar](36) NOT NULL,
	[WarehouseName] [nvarchar](150) NULL,
	[WarehouseShortName] [nvarchar](10) NULL,
	[_SourceWarehouseKey] [int] NULL,
	[_SourceSiteCode] [nvarchar](2) NULL,
	[ValidFrom] [datetime] NULL,
	[ValidTo] [datetime] NULL,
	[LastLoadedDateTime] [datetime] NULL,
 CONSTRAINT [PK_DimWarehouse] PRIMARY KEY CLUSTERED 
(
	[WarehouseKey] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[DimWarehouse]  WITH CHECK ADD  CONSTRAINT [FK_DimBranch_DimWarehouse] FOREIGN KEY([BranchKey])
REFERENCES [dbo].[DimBranch] ([BranchKey])
GO

ALTER TABLE [dbo].[DimWarehouse] CHECK CONSTRAINT [FK_DimBranch_DimWarehouse]
GO


