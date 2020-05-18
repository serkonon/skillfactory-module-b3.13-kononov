class Tag:
    def __init__(self, tag, **kwargs):
        self.tag = tag
        self.classes = ""
        self.attrs = []
        self.text = ""
        self.parent = None
        self.children = []
        self.is_single = False

        # Из параметров парсим классы и атрибуты
        for key, value in kwargs.items():
            if key == "klass":
                self.classes = \
                    str(value).strip("(").strip(")").replace(",", "").\
                        replace("'", "").replace('"', '')
            elif key == "is_single":
                if str(value).lower() == "true":
                    self.is_single = True
            else:
                self.attrs.append('{}="{}"'.format(str(key).replace("_", "-"), value))

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
        # Найдем уровень вложенности тега и определим отступ при печати
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
            tag_beg.append('class="{}"'.format(self.classes))

        if self.attrs:
            tag_beg.append(" ".join(self.attrs))

        html = indent + " ".join(tag_beg)

        if (not self.children and not self.text) or self.is_single:
            html += " />"
        else:
            html += ">"

        if self.children:
            for child in self.children:
                html += "\n" + str(child)
            html += "\n" + indent + "</{}>".format(self.tag)
        elif self.text:
            html += self.text + "</{}>".format(self.tag)

        return html

class HTML(Tag):
    def __init__(self, output=None):
        # Если output=None - вывод в консоль
        # иначе - это имя файла вывода
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
    pass

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

                with Tag("img", is_single=True, src="/icon.png", data_image="responsive") as img:
                    div += img

                body += div

            doc += body