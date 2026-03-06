source "https://rubygems.org"
ruby "3.2.0"

gem "jekyll", "~> 4.3.0"
gem "github-pages", group: :jekyll_plugins

group :jekyll_plugins do
  gem "jekyll-feed", "~> 0.12"
  gem "jekyll-seo-tag"
  gem "jekyll-sitemap"
  gem "jekyll-paginate-v2"
  gem "jekyll-redirect-from"
end

platforms :mingw, :x64_mingw, :mswin, :jemalloc do
  gem "tzinfo", "~> 1.2"
  gem "tzinfo-data"
end

gem "wdm", "~> 0.1.1", :platforms => [:mingw, :x64_mingw, :mswin]
gem "webrick", "~> 1.7"
