/****** Object:  Table [dbo].[FactInvoice]    Script Date: 12/11/2025 5:50:47 pm ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[FactInvoice](
	[FactInvoiceKey] [int] IDENTITY(1,1) NOT NULL,
	[InvoiceNumberKey] [nvarchar](20) NOT NULL,
	[InvoiceLineNumberKey] [nvarchar](20) NOT NULL,
	[SiteKey] [int] NOT NULL,
	[CustomerKey] [int] NOT NULL,
	[WarehouseKey] [int] NOT NULL,
	[ProductKey] [int] NOT NULL,
	[InvoiceDateKey] [int] NOT NULL,
	[InvoiceDate] [datetime2](7) NOT NULL,
	[DeliveryDate] [datetime2](7) NULL,
	[InvUOM] [nvarchar](10) NULL,
	[OrdUOM] [nvarchar](10) NULL,
	[PackSize] [nvarchar](30) NULL,
	[OrderedQuantity] [decimal](18, 4) NULL,
	[OrderedUOMInvQty] [decimal](18, 4) NULL,
	[UnitPrice] [money] NULL,
	[OrderedUOMUnitPrice] [money] NULL,
	[ExtendedPrice] [money] NULL,
	[LineItemTax] [decimal](18, 6) NULL,
	[Freight] [decimal](18, 6) NULL,
	[OthCharges] [decimal](18, 6) NULL,
	[InvoiceTotal] [money] NULL,
	[InvoiceTax] [money] NULL,
	[CustomerRebatePercent] [decimal](18, 6) NULL,
	[ClaimBack] [decimal](18, 6) NULL,
	[Cost] [decimal](18, 6) NULL,
	[LineItemMargin] [money] NULL,
	[CusRef] [nvarchar](50) NULL,
	[OurRef] [nvarchar](50) NULL,
	[LastLoadedDateTime] [datetime2](7) NULL,
	[CustomerRebateAmount] [decimal](18, 6) NULL,
	[LineItemMarginPercent] [decimal](18, 6) NULL,
 CONSTRAINT [PK_FactInvoice] PRIMARY KEY NONCLUSTERED 
(
	[FactInvoiceKey] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[FactInvoice] ADD  CONSTRAINT [DF_FactInvoice_CustomerRebatePercent]  DEFAULT ((0)) FOR [CustomerRebatePercent]
GO

ALTER TABLE [dbo].[FactInvoice] ADD  CONSTRAINT [DF_FactInvoice_ClaimBack]  DEFAULT ((0)) FOR [ClaimBack]
GO

ALTER TABLE [dbo].[FactInvoice] ADD  CONSTRAINT [DF_FactInvoice_Cost]  DEFAULT ((0)) FOR [Cost]
GO

ALTER TABLE [dbo].[FactInvoice] ADD  CONSTRAINT [DF_FactInvoice_LineItemMargin]  DEFAULT ((0)) FOR [LineItemMargin]
GO

ALTER TABLE [dbo].[FactInvoice]  WITH CHECK ADD  CONSTRAINT [FK_FactInvoice_DimCustomer] FOREIGN KEY([CustomerKey])
REFERENCES [dbo].[DimCustomer] ([CustomerKey])
GO

ALTER TABLE [dbo].[FactInvoice] CHECK CONSTRAINT [FK_FactInvoice_DimCustomer]
GO

ALTER TABLE [dbo].[FactInvoice]  WITH CHECK ADD  CONSTRAINT [FK_FactInvoice_DimDate] FOREIGN KEY([InvoiceDateKey])
REFERENCES [dbo].[DimDate] ([DateKey])
GO

ALTER TABLE [dbo].[FactInvoice] CHECK CONSTRAINT [FK_FactInvoice_DimDate]
GO

ALTER TABLE [dbo].[FactInvoice]  WITH CHECK ADD  CONSTRAINT [FK_FactInvoice_DimProduct] FOREIGN KEY([ProductKey])
REFERENCES [dbo].[DimProduct] ([ProductKey])
GO

ALTER TABLE [dbo].[FactInvoice] CHECK CONSTRAINT [FK_FactInvoice_DimProduct]
GO

ALTER TABLE [dbo].[FactInvoice]  WITH CHECK ADD  CONSTRAINT [FK_FactInvoice_DimSite] FOREIGN KEY([SiteKey])
REFERENCES [dbo].[DimSite] ([SiteKey])
GO

ALTER TABLE [dbo].[FactInvoice] CHECK CONSTRAINT [FK_FactInvoice_DimSite]
GO

ALTER TABLE [dbo].[FactInvoice]  WITH CHECK ADD  CONSTRAINT [FK_FactInvoice_DimWarehouse] FOREIGN KEY([WarehouseKey])
REFERENCES [dbo].[DimWarehouse] ([WarehouseKey])
GO

ALTER TABLE [dbo].[FactInvoice] CHECK CONSTRAINT [FK_FactInvoice_DimWarehouse]
GO


