import pytest
from app.parser import CSVParser

def test_csv_parser_valid_file():
    sample_csv = b"""sep=^
Task ID^Storage Interval^Operator ID^Message Length (secs)^Start Time^Stop Time^Threshold Method^Duration^Station Name^All Single Channels^Location (lat)^Location (lon)^Antenna^Polarization
1924^15 secs^UPT-LAMPUNG^15^12/15/2025 7:30:00 AM^12/15/2025 8:00:01 AM^Fixed 1 dBuV/m^Fixed: 30 mins^Bandar Lampung^No^-5.357882^105.216545^Vertical Ref^Vertical

Band #^Start Frequency (MHz)^Stop Frequency (MHz)^Bandwidth (kHz)
1^87.000000^108.000000^50.00000
2^108.000000^137.000000^6.25000

Channel No.^Frequency (MHz)^Maximum Field Strength (dBuV/m)^Average Field Strength (dBuV/m)
1^87.000000^44^36
2^87.050000^47^43
3^87.100000^47^44
"""
    
    parser = CSVParser(sample_csv)
    result = parser.parse()
    
    assert result['metadata']['Task ID'] == '1924'
    assert result['metadata']['Station Name'] == 'Bandar Lampung'
    assert len(result['bands']) == 2
    assert result['bands'][0]['start_freq'] == 87.0
    assert result['bands'][0]['stop_freq'] == 108.0
    assert len(result['channels']) == 3
    assert result['channels'][0]['frequency'] == 87.0
    assert result['channels'][0]['avg_field_strength'] == 36

def test_csv_parser_invalid_separator():
    invalid_csv = b"""Task ID,Operator
1924,UPT-LAMPUNG"""
    
    parser = CSVParser(invalid_csv)
    with pytest.raises(ValueError, match="Invalid CSV format"):
        parser.parse()

def test_csv_parser_missing_sections():
    invalid_csv = b"""sep=^
Task ID^Operator
1924^UPT-LAMPUNG"""
    
    parser = CSVParser(invalid_csv)
    with pytest.raises(ValueError, match="missing required sections"):
        parser.parse()
