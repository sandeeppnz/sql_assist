/****** Object:  Table [dbo].[DimEmployee]    Script Date: 12/11/2025 5:47:16 pm ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[DimEmployee](
	[EmployeeKey] [int] IDENTITY(1,1) NOT NULL,
	[EmployeeName] [nvarchar](150) NULL,
	[EmployeeEmailAddress] [nvarchar](450) NULL,
	[EmployeePhone] [nvarchar](20) NULL,
	[EmployeeCode] [nvarchar](36) NULL,
	[Status] [nvarchar](20) NULL,
	[StatusShortName] [nvarchar](3) NULL,
	[_SourceUserKey] [int] NULL,
	[_SourceSiteCode] [nvarchar](2) NULL,
	[ValidFrom] [datetime2](7) NULL,
	[ValidTo] [datetime2](7) NULL,
	[LastLoadedDateTime] [datetime2](7) NULL,
 CONSTRAINT [PK_DimEmployee] PRIMARY KEY CLUSTERED 
(
	[EmployeeKey] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO


