class Tag:
    def __init__(self, tag, **kwargs):
        self.tag = tag
        self.text = ""
        self.children = []
        self.attrs = {}
        self.classes = []
        self.parent = None

        # Из параметров парсим классы и атрибуты
        for key, value in kwargs.items():
            if key == "klass":
                clss = \
                    str(value).strip("(").strip(")").replace(" ", "").replace("'", "").split(",")
                for cls in clss:
                    if cls:
                        self.classes.append(cls)
            else:
                self.attrs[key] = value

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    # Обрабатываем += класса
    def __iadd__(self, other):
        self.children.append(other)
        other.parent = self
        return self

    def __str__(self):
        # Найдем уровень вложенности тега
        toplvl = {"html", "head", "body"}
        indnt = 0
        Tag = self
        while Tag.tag not in toplvl:
            Tag = Tag.parent
            if Tag is None or indnt >= 10:
                break
            else:
                indnt += 1

        indent = " " * 4 * indnt
        tag_beg = ["<{}".format(self.tag)]

        if self.classes:
            tag_beg.append('class="' + " ".join(self.classes) + '"')

        if self.attrs:
            atrs = []
            for key, value in self.attrs.items():
                atrs.append('{0}="{1}"'.format(key,value))
            tag_beg.append(" ".join(atrs))

        html = indent + " ".join(tag_beg)

        if self.children or self.text:
            html += ">"
        else:
            html += "/>"

        if self.children:
            for child in self.children:
                html += "\n" + str(child)
            html += "\n" + indent + "</{}>".format(self.tag)
        elif self.text:
            html += self.text + "</{}>".format(self.tag)

        return html

class HTML(Tag):
    def __init__(self, output=None):
        super().__init__("html")
        self.output = output

    def __exit__(self, *args):
        html = str(self)
        if self.output is not None:
            with open(self.output, "w") as file:
                file.write(html)
        else:
            print(html)

class TopLevelTag(Tag):
    def __init__(self, tag):
        super().__init__(tag)

if __name__ == "__main__":
    with HTML(output="test.html") as doc:
        with TopLevelTag("head") as head:
            with Tag("title") as title:
                title.text = "hello"
                head += title
            doc += head

        with TopLevelTag("body") as body:
            with Tag("h1", klass=("main-text",)) as h1:
                h1.text = "Test"
                body += h1

            with Tag("div", klass=("container", "container-fluid"), id="lead") as div:
                with Tag("p") as paragraph:
                    paragraph.text = "another test"
                    div += paragraph

                with Tag("img", is_single=True, src="/icon.png") as img:
                    div += img

                body += div

            doc += body