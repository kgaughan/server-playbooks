def subdomains(domain, labels):
    return [label + '.' + domain for label in labels]


class FilterModule(object):

    def filters(self):
        return {
            'subdomains': subdomains,
        }
