# Package Deliverables Reference

**Quick reference for SYNAPSE engineering packages**

> **Detailed specs:** See [package-generation.md](../../.dev/roadmap/backlog/package-generation.md)

---

## Standard Packages

### Instrument Packages

**IN-P040 - Instrument Index**
- All field instruments (FT, PT, LT, TT, etc.)
- Tag, Type, Service, Range, Output, Cable#, IO Address
- Format: Excel, PDF

### Electrical Packages

**EL-M040 - Motor Schedule**
- All motors with HP, Voltage, RPM, Frame
- VFD requirements, MCC panel, Breaker size
- Format: Excel, PDF

**EL-V040 - VFD Schedule**
- All VFDs with ratings, manufacturers
- Control cables, communication protocols
- Format: Excel, PDF

### Cable Packages

**CA-P040 - Power Cable Schedule**
- All power cables with sizing
- From/To, Type, Length, Route
- Format: Excel, PDF

**CA-C040 - Control Cable Schedule**
- All control/signal cables
- From/To, Signals, Shielding
- Format: Excel, PDF

### IO Packages

**IO-P040 - IO List (by PLC)**
- IO allocation per PLC
- Tag, Type, Address, Signal, Cable
- Format: Excel, PDF

### BOM Packages

**BID-LST - Bill of Materials**
- Complete material list
- Quantities, Vendors, Pricing
- Format: Excel

---

## Generation Methods

### One-Click Generation
1. Navigate to Packages
2. Select package type (IN-P040, EL-M040, etc.)
3. Choose format (Excel and/or PDF)
4. Click **[Generate]**
5. Download automatically

### Batch Generation
1. Select multiple packages
2. Choose formats
3. Click **[Generate All]**
4. Downloads as ZIP file

---

## Template Customization

**Built-in Templates:**
- Company logo and header
- Standard formatting
- CEC/NEC compliance notes

**Custom Templates:**
- Upload your Excel template
- Map data fields
- Save as project template

---

## Related Documentation

- [Package Generation (Technical)](../../.dev/roadmap/backlog/package-generation.md)
- [Package Generation Workflow](../workflows/package-generation.md)

---

**Updated:** 2025-11-24
