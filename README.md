## compiling data for fragrance making

TGSC is a web repository for fragrance ingredients, suppliers and other fragrance-making topics. It has been around since the 90s and has a sprawling amount of data distributed across individual webpages in html tags. In order to have a working database for a future fragrance formulation app, the scattered data needs to be compiled in a single place.

- [ ] crawling TGSC website
- [ ] compiling in database
- [ ] flutter app development

# crawling TGSC
1. has an 'all chemicals' page, that divides all the available chemicals alphabetically. So /all_chemicals_a, /all_chemicals_b, etc. This list is the first to tackle by compiling a list of working links (there may be some letters that don't work)

2. Each letter page has all the chemicals available for that particular letter on good scents (no further pagination), so one could compile a list of chemicals per alphabet letter and the direct link to each.  

3. Each chemical page has many poorly (in terms of html tags) divided categories. Ones that may be useful: chemical name, alternate names, cas number, organoleptic qualities, physico-chemical qualities, suppliers

4. Some other sites may have to be crawled to get prices. Once crawling scripts are developed and the database is deployed, some automated pulls may keep the prices up to date on a weekly basis.
