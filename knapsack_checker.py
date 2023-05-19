from urllib.parse import urlparse

with open('resources/c_sites.txt', 'r') as f:
    c_sites = f.read().split('\n')

with open('resources/c_sites_weights.txt', 'r') as f:
    site_weights = f.read().split('\n')
    # reverses weights so that more credible sites are lighter and fit into knapsack
    site_weights.reverse()

sites_weights = {}

for site, weight in zip(c_sites, site_weights):
    sites_weights[site] = int(float(weight))

#helper functions
#gets the main domain of a url, for example: https://www.cnnphilippines.com/
def get_domain(url):
    if type(url) == str:
        parsed_uri = urlparse(f'{url}')
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        return domain
    if type(url) == list:
        urls = []
        for i in url:
            parsed_uri = urlparse(f'{i}')
            domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
            urls.append(domain)

        return urls

#gets the key when given a value from a dictionary
def get_key(val, my_dict):
    if type(val) == int:
        for key, value in my_dict.items():
            if val == value:
                return key
    if type(val) == list:
        keys = []
        for v in val:
            for key, value in my_dict.items():
                if v == value:
                    keys.append(key)
        return keys

    return "key doesn't exist"

#main knapsack class for fact checking
class KnapsackChecker:
    def __init__(self, sim_vals, urls):
        self.sim_vals = sim_vals
        self.urls = urls
    #checker function to initialize all inputs to knapsack and output its results along with the credible sites

    def checker(self):
        # max_vals_sites = []
        domains = get_domain(self.urls)
        #if the domain is not part of the credible sites dictionary,
        # it will give it a heavy weight so it doesn't get included in the algorithm
        for domain in domains:
            if domain not in sites_weights:
                sites_weights[domain] = 200
        # gets the weights from the dictionary
        domain_weights = [sites_weights[domain] for domain in domains]
        n_searches = len(self.urls)
        #the knapsack algorithm here outputs the chosen items too so that we know what sites it picked
        res_url_wts, res_sim = self.knapsack(98, domain_weights, self.sim_vals, n_searches)
        # gets corresponding domains of those weights the knapsack algorithm picked
        res_urls = get_key(res_url_wts, sites_weights)
        # also gets the full sites of those domains
        full_res_sites = [y for x in res_urls for y in self.urls if x in y]

        return res_url_wts, res_sim, full_res_sites

    # main knapsack algorithm
    def knapsack(self, max_wt, wt, val, n):
        K = [[0 for w in range(max_wt + 1)] for i in range(n + 1)]

        # build table K[][] in bottom up manner
        for i in range(n + 1):
            for w in range(max_wt + 1):
                if i == 0 or w == 0:
                    K[i][w] = 0
                elif wt[i - 1] <= w:
                    K[i][w] = max(val[i - 1]
                                  + K[i - 1][w - wt[i - 1]],
                                  K[i - 1][w])
                else:
                    K[i][w] = K[i - 1][w]

        # stores the result of Knapsack
        res = K[n][max_wt]
        re = res
        items = []

        w = max_wt
        for i in range(n, 0, -1):
            if re <= 0:
                break
            # either the result comes from the top (K[i-1][w]) or from (val[i-1] + K[i-1] [w-wt[i-1]]) as in Knapsack table
            # if it comes from the latter one/ it means the item is included.
            if re == K[i - 1][w]:
                continue
            else:
                # this item is included.
                items.append(wt[i - 1])

                # since this weight is included, its value is deducted
                re = re - val[i - 1]
                w = w - wt[i - 1]
        return items, res

    def truth_checker_k(self, s, w, t=1.18, l=2):
        if s >= t and w >= l:
            return 'Real'
        elif s > 0.45 and w < l:
            return 'Real'
        elif s < t and w >= l:
            return 'Risky'
        else:
            return 'Risky'

