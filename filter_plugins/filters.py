def subdomains(domain, labels):
    return [label + "." + domain for label in labels]


def acme_list(domain, labels):
    return [domain] + subdomains(domain, labels)


class FilterModule(object):
    def filters(self):
        return {"subdomains": subdomains, "acme_list": acme_list}
