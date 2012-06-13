try:
    from lxml import etree
except ImportError:
    try:
        import xml.etree.cElementTree as etree
    except (ImportError, SystemError):
        import xml.etree.ElementTree as etree
