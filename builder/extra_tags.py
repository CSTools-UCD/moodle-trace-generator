from typing import List, Any
from dominate.tags import html_tag, unicode
from dominate.util import escape, unescape

class embeddedfile(html_tag):
  def render(self, indent: str='  ' , pretty:bool=True, xhtml:bool=False) -> str:
    data = self._render([], 0, indent, pretty, xhtml)
    return u''.join(data)

  def _render(self, sb: List[str], indent_level :int, indent_str: str, pretty: bool, xhtml: bool) -> List[str]:
    pretty = pretty and self.is_pretty

    name = getattr(self, 'tagname', type(self).__name__)

    # Workaround for python keywords and standard classes/methods
    # (del, object, input)
    name = "file"

    # open tag
    sb.append('<')
    sb.append(name)

    for attribute, value in sorted(self.attributes.items()):
      if value is not False: # False values must be omitted completely
          sb.append(' %s="%s"' % (attribute, escape(unicode(value), True)))

    sb.append(' />' if self.is_single and xhtml else '>')

    if not self.is_single:
      inline = self._render_children(sb, indent_level + 1, indent_str, pretty, xhtml)

      if pretty and not inline:
        sb.append('\n')
        sb.append(indent_str * indent_level)

      # close tag
      sb.append('</')
      sb.append(name)
      sb.append('>')

    return sb

class quiz(html_tag):
  pass

class question(html_tag):
  pass

class name(html_tag):
  pass
class tspan(html_tag):
  pass
class penalty(html_tag):
  pass

class hidden(html_tag):
  pass

class generalfeedback(html_tag):
  pass

class questiontext(html_tag):
  pass

class category(html_tag):
  pass

class info(html_tag):
  pass

class questiontextT(html_tag):
  def _render(self, sb :List[str], indent_level : int, indent_str : str, pretty : bool, xhtml: bool) -> List[str]:
    pretty = pretty and self.is_pretty
    name = "text"
    sb.append('<')
    sb.append(name)
    sb.append(' />' if self.is_single and xhtml else '>')
    sb.append('<![CDATA[')

    inline = self._render_children(sb, indent_level + 1, indent_str, pretty, xhtml)

    if pretty and not inline:
      sb.append('\n')
      sb.append(indent_str * indent_level)

    sb.append(']]>')
    sb.append('</')
    sb.append("text")
    sb.append('>')
    
    return sb

class scrpt(html_tag):
  def render(self, indent: str='  ' , pretty:bool=True, xhtml:bool=False) -> str:
    data = self._render([], 0, indent, pretty, xhtml)
    return u''.join(data)

  def _render(self, sb: List[str], indent_level :int, indent_str: str, pretty: bool, xhtml: bool) -> List[str]:
    pretty = pretty and self.is_pretty
    name = getattr(self, 'tagname', type(self).__name__)
    sb.append('<script type="text/javascript">')
    sb.append(unescape(self.children[0]))
    sb.append('</script>')  
    print(sb)
    return sb

class tgs(html_tag):
  def _render(self, sb : List[str], indent_level : int, indent_str : str, pretty : bool, xhtml : bool) -> List[str]:
    pretty = pretty and self.is_pretty
    name = "tags"
    sb.append('<')
    sb.append(name)
    sb.append(' />' if self.is_single and xhtml else '>')
    inline = self._render_children(sb, indent_level + 1, indent_str, pretty, xhtml)

    if pretty and not inline:
      sb.append('\n')
      sb.append(indent_str * indent_level)
    sb.append('</')
    sb.append(name)
    sb.append('>')
    
    return sb

class tag(html_tag):
  pass

class svg(html_tag):
  pass

class g(html_tag):
  pass

class defs(html_tag):
  pass

class CDATA(html_tag):
  def render(self, indent: str='  ' , pretty:bool=True, xhtml:bool=False) -> str:
    data = self._render([], 0, indent, pretty, xhtml)
    return u''.join(data)

  def _render(self, sb: List[str], indent_level :int, indent_str: str, pretty: bool, xhtml: bool) -> List[str]:
    pretty = pretty and self.is_pretty
    name = getattr(self, 'tagname', type(self).__name__)
    sb.append('<![CDATA[')
    sb.append(unescape(self.children[0]))
    sb.append(']]>')  

    return sb

class rect(html_tag):
  def __init__(self, **kwargs : Any) -> None:
        self.is_single = True
        super().__init__(**kwargs)

class text(html_tag):
  def _render(self, sb : List[str], indent_level : int, indent_str : str, pretty : bool, xhtml : bool) -> List[str]:
    pretty = pretty and self.is_pretty
    name = getattr(self, 'tagname', type(self).__name__)
    if name[-1] == '_':
      name = name[:-1]
    sb.append('<')
    sb.append(name)

    for attribute, value in sorted(self.attributes.items()):
      if value is not False: # False values must be omitted completely
          sb.append(' %s="%s"' % (attribute.replace('_', '-'), escape(unicode(value), True)))

    sb.append(' />' if self.is_single and xhtml else '>')

    if not self.is_single:
      inline = self._render_children(sb, indent_level + 1, indent_str, pretty, xhtml)

      if pretty and not inline:
        sb.append('\n')
        sb.append(indent_str * indent_level)

      sb.append('</')
      sb.append(name)
      sb.append('>')

    return sb