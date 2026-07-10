
/* ══════════════════════════════════════════════
   Translations (i18n)
   ══════════════════════════════════════════════ */
const TRANSLATIONS = {
  en: {
    navTrends: 'Google Trends', navBingTrends: 'Bing Trends', navTechnical: 'Technical SEO', navBing: 'Bing SEO', navSettings: 'Settings',
    dashboard: 'Dashboard', keywordResearch: 'Keyword Research', pillarCluster: 'Pillar-Cluster Map',
    articleGenerator: 'Article Generator', contentCalendar: 'Content Calendar',
    seoAudit: 'SEO Audit', batchAudit: 'Batch Audit', aiRecommendations: 'AI Recommendations',
    keywordTracking: 'Keyword Tracking', auditHistory: 'Audit History',
    auditHistoryEmpty: 'No audit history yet. Run an SEO audit to start tracking.',
    googleTrends: 'Google Trends', bingSeoTitle: 'Bing SEO Compatibility',
    changePassword: 'Change Password', userManagement: 'User Management', preferences: 'Preferences',
    currentPassword: 'Current Password', newPassword: 'New Password', updatePassword: 'Update Password',
    username: 'Username', password: 'Password', role: 'Role', createUser: 'Create User', noUsers: 'No users found.',
    defaultLanguage: 'Default Language', defaultAiProvider: 'Default AI Provider', theme: 'Theme',
    keywords: 'Keywords (comma separated)', geo: 'Geography',
    viewTrends: 'View Trends', interestOverTime: 'Interest Over Time',
    relatedQueries: 'Related Queries', interestByRegion: 'Interest by Region',
    trendingSearches: 'Trending Searches', checking: 'Checking...', timeframe: 'Timeframe',
    urlToCheck: 'URL to Check', checkBing: 'Check Bing SEO', checkIndex: 'Check Index Status',
    submitToBing: 'Submit to Bing', seoChecks: 'SEO Checks', recommendations: 'Recommendations',
    signIn: 'Sign In', connected: 'Connected', darkMode: 'Dark Mode', lightMode: 'Light Mode',
    signOut: 'Sign Out', language: 'Language',
    generateArticle: 'Generate Article', topic: 'Topic',
    targetKeywords: 'Target Keywords (one per line)', articleLanguage: 'Article Language',
    english: 'English', persian: 'Persian (Farsi)',
    searchForTrends: 'Search trends for your keywords alongside research',
    noTrendsData: 'No trends data available. Enter keywords above.',
    noBingChecks: 'Run a Bing SEO check to see results.',
    noRecommendations: 'No recommendations for this page.',
    noAi: 'No AI',
    working: 'Working...',
    loginUsername: 'Username', loginPassword: 'Password', signInPrompt: 'Sign in to access SEO AI Tools',
    appSubtitle: 'SEO AI Tools', builtWith: 'Built with Python · Flask · Chart.js',
    navOverview: 'Overview', navDashboard: 'Dashboard', navResearch: 'Research',
    navKeywordResearch: 'Keyword Research', navPillarCluster: 'Pillar-Cluster Map',
    navContentGap: 'Content Gap',
    navContent: 'Content', navArticleGenerator: 'Article Generator', navContentCalendar: 'Content Calendar',
    navAnalysis: 'Analysis', navSeoAudit: 'SEO Audit', navBatchAudit: 'Batch Audit',
    navAiRecommendations: 'AI Recommendations', navTracking: 'Tracking',
    navKeywordTracking: 'Keyword Tracking', navAuditHistory: 'Audit History',
    navInsights: 'Insights', navSystem: 'System',
    keywordsFound: 'Keywords Found', clusters: 'Clusters', auditsRun: 'Audits Run', calendarEvents: 'Calendar Events',
    quickActions: 'Quick Actions', researchKeywords: 'Research Keywords',
    auditUrl: 'Audit a URL', buildClusters: 'Build Clusters',
    systemStatus: 'System Status', dbLabel: 'Database', aiProviderLabel: 'AI Provider', defaultAiLabel: 'Default AI',
    auditHistoryOverview: 'Audit History Overview', noAuditHistory: 'No audit history yet. Run an audit to see results here.',
    pageTypeBreakdown: 'Page Type Breakdown', noAudits: 'No audits yet.',
    keywordResearchTitle: 'Keyword Research', trackKeyword: 'Track Keyword',
    seedKeyword: 'Seed Keyword', depth: 'Depth', level: 'Level',
    expandModifiers: 'Expand with modifiers', startResearch: 'Start Research', exportCsv: 'Export CSV',
    intentDistribution: 'Intent Distribution', autocompleteSuggestions: 'Autocomplete Suggestions',
    peopleAlsoAsk: 'People Also Ask', relatedSearches: 'Related Searches', serpResults: 'SERP Results',
    pillarClusterTitle: 'Pillar-Cluster Map', runResearchFirst: 'Run keyword research first, then come back to build your cluster map.',
    goToKeywordResearch: 'Go to Keyword Research', similarityThreshold: 'Similarity Threshold',
    threshold: 'Threshold', buildMap: 'Build Map', clusterSizes: 'Cluster Sizes',
    articleGeneratorTitle: 'Article Generator', aiProvider: 'AI Provider',
    wordCount: 'Word Count', tone: 'Tone', style: 'Style',
    generateArticleBtn: 'Generate Article', generatedArticle: 'Generated Article',
    copy: 'Copy', downloadMd: 'Download .md',
    seoAuditTitle: 'SEO Audit', urlToAudit: 'URL to Audit', focusKeyword: 'Focus Keyword (optional)',
    pageType: 'Page Type', autoDetect: 'Auto-detect from URL', genericPage: 'General Page',
    homepagePage: 'Homepage / Main Page', productPage: 'Product / Service Page', blogPage: 'Blog / Article Page',
    runAudit: 'Run Audit', exportPdf: 'Export PDF',
    batchAuditTitle: 'Batch Audit', sampleCsv: 'Sample CSV',
    uploadCsv: 'Upload CSV (columns: url, keyword, page_type)',
    optionalColumns: 'Optional columns: keyword, page_type (homepage/product/blog/generic/auto)',
    runBatchAudit: 'Run Batch Audit',
    aiSeoRecommendations: 'AI SEO Recommendations',
    runAuditFirst: 'Run an SEO audit first to get AI-powered recommendations.',
    goToSeoAudit: 'Go to SEO Audit', quickWins: 'Quick Wins',
    aiPoweredAnalysis: 'AI-Powered Analysis', generateAiRecommendations: 'Generate AI Recommendations',
    keywordTrackingTitle: 'Keyword Tracking',
    contentCalendarTitle: 'Content Calendar', generateFromClusters: 'Generate from Clusters',
    exportMd: 'Export MD', exportJson: 'Export JSON',
    buildClusterFirst: 'Build a pillar-cluster map first, then generate your content calendar.',
    goToClusters: 'Go to Clusters', clusterTrends: 'Google Trends Data',
    bingTrendsTitle: 'Bing Search Trends',
    viewBingTrends: 'View Bing Trends',
    bingInterestOverTime: 'Interest Over Time',
    bingTopQueries: 'Top Related Queries',
    bingTrendingSearches: 'Bing Trending Searches',
    noBingTrends: 'Enter keywords above to see Bing search trends.',
    autoPipeline: 'Auto-generate content plan',
    pipelineRunning: 'Running SEO Pipeline...',
    pipelineStep1: 'Keyword Research',
    pipelineStep2: 'Building Pillar-Cluster Map',
    pipelineStep3: 'AI Analysis & Content Plan',
    pipelineStatus: 'Preparing...',
    useClusterTopics: 'Use Cluster Topics',
      
    selectArticlesToGenerate: 'Select Articles to Generate',
    generateSelected: 'Generate Selected',
    selected: 'selected',
    selectAll: 'Select All',
    deselectAll: 'Deselect All',
    cancel: 'Cancel',
    generatedArticles: 'Generated Articles',
    expandAll: 'Expand All',
    collapseAll: 'Collapse All',
    done: 'Done',
    failed: 'Failed',
    noClusterArticles: 'No articles found in the content plan.',
    useLlmIntel: 'Use LLM Intelligence',
    llmCapabilities: 'LLM Capabilities',
    keywordDifficulty: 'Keyword Difficulty',
    useSemanticClustering: 'Semantic (LLM)',
    cachedData: 'Restored from local cache',
    refresh: 'Refresh',
    contentGapTitle: 'تحلیل شکافت موضوعی',
    contentGapDesc: 'موضوعی را که رقابتان توجه در نتیجه رد ظاهر میکنند',
    contentGapSeedLabel: 'کلمه کلیدی هدف',
    contentGapSeedPlaceholder: 'مثلًا seo tools',
    contentGapCompetitorsLabel: 'آدرس رقکابتان (هر صفحه بر یک خط)',
    contentGapCompetitorsPlaceholder: 'https://competitor1.com\nhttps://competitor2.com',
    contentGapMyKeywordsLabel: 'کلمات کلیدی شما (هر صفحه بر یک خط)',
    contentGapMyKeywordsPlaceholder: 'خالی بگذارید برای استفاده از دادهای کلمه کلیدی',
    contentGapAnalyzeBtn: 'تحلیل شکافت موضوعی',
    contentGapDiscoverBtn: 'کشف رقڨات',
    contentGapResultsTitle: 'نتایج تحلیل',
    contentGapKeywordsTitle: 'کلمات کلیدی يافته شده',
    contentGapGapsTitle: 'شکافت‌های موضوعی',
    contentGapCoverageTitle: 'پوشایش',
    contentGapOpportunity: 'امکان',
    contentGapFrequency: 'تکرار',
    contentGapCompetitorsUsing: 'رقباتان استفاده از',
    contentGapNoResults: 'شکافتی یافته نشد! محتواوت شما کلمات رقباتان را کامل کرده است.',
    contentGapLoading: 'در حال تحلیل مقالات رقبتان...',
    contentGapExportBtn: 'خروج CSV',
    contentGapTitle: 'Content Gap Analysis',
    contentGapDesc: 'Find topics your competitors rank for that you don\'t',
    contentGapSeedLabel: 'Target Keyword',
    contentGapSeedPlaceholder: 'e.g. seo tools',
    contentGapCompetitorsLabel: 'Competitor URLs (one per line, optional)',
    contentGapCompetitorsPlaceholder: 'https://competitor1.com\nhttps://competitor2.com',
    contentGapMyKeywordsLabel: 'Your Keywords (one per line, optional)',
    contentGapMyKeywordsPlaceholder: 'Leave empty to use keyword research data',
    contentGapAnalyzeBtn: 'Analyze Content Gaps',
    contentGapDiscoverBtn: 'Discover Competitors',
    contentGapResultsTitle: 'Gap Analysis Results',
    contentGapKeywordsTitle: 'Keywords Found',
    contentGapGapsTitle: 'Content Gaps',
    contentGapCoverageTitle: 'Coverage',
    contentGapOpportunity: 'Opportunity',
    contentGapFrequency: 'Frequency',
    contentGapCompetitorsUsing: 'Competitors Using',
    contentGapNoResults: 'No content gaps found. Your content covers competitor keywords well!',
    contentGapLoading: 'Analyzing competitor content...',
    contentGapExportBtn: 'Export Gaps CSV',
    llmCapabilities: 'قابلیت‌های هوش مصنوعی',
    technicalSeoTitle: 'سئوی فنی',
    fullTechnicalAudit: 'احتمام کامل سئوی فنی',
    techOverallScore: 'امتیاز کلی',
    techIssues: 'مشکلات',
    techRobotsTxt: 'robots.txt',
    techSitemap: 'sitemap',
    techStructuredData: 'دادهای ساختاری',
    techWebVitals: 'شاخصات اصلی وب',
    noBingTrends: 'کلمات کلیدی را در بالا وارد کنید تا روندهای جستجوی بینگ را ببینید.'
},
  fa: {
    navTrends: 'روندهای گوگل', navBingTrends: 'روندهای بینگ', navBing: 'سئوی بینگ', navTechnical: 'سئوی فنی', navSettings: 'تنظیمات',
    dashboard: 'داشبورد', keywordResearch: 'تحقیق کلمات کلیدی', pillarCluster: 'نقشه ستون-خوشه',
    articleGenerator: 'تولید مقاله', contentCalendar: 'تقویم محتوا',
    seoAudit: 'سئوی سایت', batchAudit: 'سئوی دسته‌جمعی', aiRecommendations: 'توصیه‌های هوش مصنوعی',
    keywordTracking: 'ردیابی کلمات کلیدی', auditHistory: 'تاریخچه سئو',
    auditHistoryEmpty: 'هنوز تاریخچه سئویی وجود ندارد. یک سئوی URL انجام دهید.',
    googleTrends: 'روندهای گوگل', bingSeoTitle: 'سازگاری با سئوی بینگ',
    changePassword: 'تغییر رمز عبور', userManagement: 'مدیریت کاربران', preferences: 'تنظیمات شخصی',
    currentPassword: 'رمز عبور فعلی', newPassword: 'رمز عبور جدید', updatePassword: 'به‌روزرسانی رمز',
    username: 'نام کاربری', password: 'رمز عبور', role: 'نقش', createUser: 'ایجاد کاربر', noUsers: 'هیچ کاربری یافت نشد.',
    defaultLanguage: 'زبان پیش‌فرض', defaultAiProvider: 'ارائه‌دهنده پیش‌فرض هوش مصنوعی', theme: 'پوسته',
    keywords: 'کلمات کلیدی (جدا شده با کاما)', geo: 'موقعیت جغرافیایی',
    viewTrends: 'مشاهده روندها', interestOverTime: 'علاقه در طول زمان',
    relatedQueries: 'جستجوهای مرتبط', interestByRegion: 'علاقه بر اساس منطقه',
    trendingSearches: 'جستجوهای پرطرفدار', checking: 'در حال بررسی...', timeframe: 'بازه زمانی',
    urlToCheck: 'URL برای بررسی', checkBing: 'بررسی سئوی بینگ', checkIndex: 'بررسی وضعیت نمایه',
    submitToBing: 'ارسال به بینگ', seoChecks: 'بررسی‌های سئو', recommendations: 'توصیه‌ها',
    signIn: 'ورود', connected: 'متصل', darkMode: 'حالت تاریک', lightMode: 'حالت روشن',
    signOut: 'خروج', language: 'زبان',
    generateArticle: 'تولید مقاله', topic: 'موضوع',
    targetKeywords: 'کلمات کلیدی هدف (هر خط یک کلمه)', articleLanguage: 'زبان مقاله',
    english: 'انگلیسی', persian: 'فارسی',
    searchForTrends: 'روندهای جستجوی کلمات کلیدی خود را در کنار تحقیق مشاهده کنید',
    noTrendsData: 'داده‌ای برای روندها موجود نیست. کلمات کلیدی را وارد کنید.',
    noBingChecks: 'برای مشاهده نتایج، یک بررسی سئوی بینگ اجرا کنید.',
    noRecommendations: 'هیچ توصیه‌ای برای این صفحه وجود ندارد.',
    noAi: 'هوش مصنوعی در دسترس نیست',
    working: 'در حال انجام...',
    loginUsername: 'نام کاربری', loginPassword: 'رمز عبور', signInPrompt: 'برای دسترسی به ابزارهای سئو وارد شوید',
    appSubtitle: 'ابزارهای هوشمند سئو', builtWith: 'ساخته شده با Python · Flask · Chart.js',
    navOverview: 'نمای کلی', navDashboard: 'داشبورد', navResearch: 'تحقیق',
    navKeywordResearch: 'تحقیق کلمات کلیدی', navPillarCluster: 'نقشه ستون-خوشه',
    navContentGap: 'تحلیل شکافت موضوعی',
    navContent: 'محتوا', navArticleGenerator: 'تولید مقاله', navContentCalendar: 'تقویم محتوا',
    navAnalysis: 'تحلیل', navSeoAudit: 'سئوی سایت', navBatchAudit: 'سئوی دسته‌جمعی',
    navAiRecommendations: 'توصیه‌های هوش مصنوعی', navTracking: 'ردیابی',
    navKeywordTracking: 'ردیابی کلمات کلیدی', navAuditHistory: 'تاریخچه سئو',
    navInsights: 'تحلیل‌ها', navSystem: 'سیستم',
    keywordsFound: 'کلمات کلیدی یافت شده', clusters: 'خوشه‌ها', auditsRun: 'سئوهای انجام شده', calendarEvents: 'رویدادهای تقویم',
    quickActions: 'اقدامات سریع', researchKeywords: 'تحقیق کلمات کلیدی',
    auditUrl: 'سئوی یک URL', buildClusters: 'ساخت خوشه‌ها',
    systemStatus: 'وضعیت سیستم', dbLabel: 'پایگاه داده', aiProviderLabel: 'ارائه‌دهنده هوش مصنوعی', defaultAiLabel: 'هوش مصنوعی پیش‌فرض',
    auditHistoryOverview: 'نمای کلی تاریخچه سئو', noAuditHistory: 'هنوز تاریخچه سئویی وجود ندارد. یک سئو انجام دهید.',
    pageTypeBreakdown: 'تفکیک نوع صفحه', noAudits: 'هنوز سئویی انجام نشده.',
    keywordResearchTitle: 'تحقیق کلمات کلیدی', trackKeyword: 'ردیابی کلمه کلیدی',
    seedKeyword: 'کلمه کلیدی اولیه', depth: 'عمق', level: 'سطح',
    expandModifiers: 'گسترش با اصلاح‌کننده‌ها', startResearch: 'شروع تحقیق', exportCsv: 'خروجی CSV',
    intentDistribution: 'توزیع هدف', autocompleteSuggestions: 'پیشنهادات تکمیل خودکار',
    peopleAlsoAsk: 'سوالات مشابه', relatedSearches: 'جستجوهای مرتبط', serpResults: 'نتایج SERP',
    pillarClusterTitle: 'نقشه ستون-خوشه', runResearchFirst: 'ابتدا تحقیق کلمات کلیدی را انجام دهید، سپس به اینجا برگردید.',
    goToKeywordResearch: 'برو به تحقیق کلمات کلیدی', similarityThreshold: 'آستانه شباهت',
    threshold: 'آستانه', buildMap: 'ساخت نقشه', clusterSizes: 'اندازه خوشه‌ها',
    articleGeneratorTitle: 'تولید مقاله', aiProvider: 'ارائه‌دهنده هوش مصنوعی',
    wordCount: 'تعداد کلمات', tone: 'لحن', style: 'سبک',
    generateArticleBtn: 'تولید مقاله', generatedArticle: 'مقاله تولید شده',
    copy: 'کپی', downloadMd: 'دانلود .md',
    seoAuditTitle: 'سئوی سایت', urlToAudit: 'URL برای سئو', focusKeyword: 'کلمه کلیدی (اختیاری)',
    pageType: 'نوع صفحه', autoDetect: 'تشخیص خودکار از URL', genericPage: 'صفحه عمومی',
    homepagePage: 'صفحه اصلی', productPage: 'صفحه محصول/خدمات', blogPage: 'صفحه وبلاگ/مقاله',
    runAudit: 'اجرای سئو', exportPdf: 'خروجی PDF',
    batchAuditTitle: 'سئوی دسته‌جمعی', sampleCsv: 'نمونه CSV',
    uploadCsv: 'آپلود CSV (ستون‌ها: url, keyword, page_type)',
    optionalColumns: 'ستون‌های اختیاری: keyword, page_type (homepage/product/blog/generic/auto)',
    runBatchAudit: 'اجرای سئوی دسته‌جمعی',
    aiSeoRecommendations: 'توصیه‌های هوش مصنوعی سئو',
    runAuditFirst: 'ابتدا یک سئوی URL انجام دهید تا توصیه‌های هوش مصنوعی دریافت کنید.',
    goToSeoAudit: 'برو به سئوی URL', quickWins: 'بردهای سریع',
    aiPoweredAnalysis: 'تحلیل با هوش مصنوعی', generateAiRecommendations: 'تولید توصیه‌های هوش مصنوعی',
    keywordTrackingTitle: 'ردیابی کلمات کلیدی',
    contentCalendarTitle: 'تقویم محتوا', generateFromClusters: 'تولید از خوشه‌ها',
    exportMd: 'خروجی MD', exportJson: 'خروجی JSON',
    buildClusterFirst: 'ابتدا نقشه ستون-خوشه را بسازید، سپس تقویم محتوا را تولید کنید.',
    goToClusters: 'برو به خوشه‌ها', clusterTrends: 'داده‌های روند گوگل',
    bingTrendsTitle: 'روندهای جستجوی بینگ',
    viewBingTrends: 'مشاهده روندهای بینگ',
    bingInterestOverTime: 'علاقه در طول زمان',
    bingTopQueries: 'جستجوهای مرتبط برتر',
    bingTrendingSearches: 'جستجوهای پرطرفدار بینگ',
    noBingTrends: 'کلمات کلیدی را وارد کنید تا روندهای جستجوی بینگ را مشاهده کنید.',
    autoPipeline: 'تولید خودکار پلان محتوایی',
    pipelineRunning: 'در حال اجرای پایپ لاین سئو...',
    pipelineStep1: 'تحقیق کلمات کلیدی',
    pipelineStep2: 'ساخت نقشه ستون-خوشه',
    pipelineStep3: 'تحلیل هوش مصنوعی و پلان محتوا',
    pipelineStatus: 'در حال آماده‌سازی...',
    useClusterTopics: 'استفاده از موضوعات خوشه',
      

    selectArticlesToGenerate: 'انتخاب مقالات برای تولید',
    generateSelected: 'تولید انتخاب شده',
    selected: 'انتخاب شده',
    selectAll: 'انتخاب همه',
    deselectAll: 'لغو انتخاب همه',
    cancel: 'لغو',
    generatedArticles: 'مقالات تولید شده',
    expandAll: 'باز کردن همه',
    collapseAll: 'بستن همه',
    done: 'انجام شد',
    failed: 'ناموفق',
    noClusterArticles: 'هیچ مقاله‌ای در پلان محتوایی یافت نشد.',
  }

};

let currentLanguage = localStorage.getItem('rankivo_lang') || 'en';

function t(key) {
  const lang = TRANSLATIONS[currentLanguage] || TRANSLATIONS.en;
  return lang[key] || TRANSLATIONS.en[key] || key;
}

function setLanguage(lang) {
  currentLanguage = lang;
  localStorage.setItem('rankivo_lang', lang);
  
  // Update html element
  document.documentElement.setAttribute('lang', lang === 'fa' ? 'fa' : 'en');
  document.documentElement.setAttribute('dir', lang === 'fa' ? 'rtl' : 'ltr');
  document.documentElement.setAttribute('data-lang', lang);
  
  // Update language switcher buttons
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.lang === lang);
  });
  
  // Update all i18n elements
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.dataset.i18n;
    el.textContent = t(key);
  });
  
  // Update page title
  const titles = {
    en: {
      dashboard: 'Dashboard', keywords: 'Keyword Research', clusters: 'Pillar-Cluster Map',
      articles: 'Article Generator', calendar: 'Content Calendar', audit: 'SEO Audit',
      batch: 'Batch Audit', recommendations: 'AI Recommendations',
      tracking: 'Keyword Tracking', history: 'Audit History',
      trends: 'Google Trends', bing: 'Bing SEO', 'bing-trends': 'Bing Trends', technical: 'Technical SEO', settings: 'Settings'
    },
    fa: {
      dashboard: 'داشبورد', keywords: 'تحقیق کلمات کلیدی', clusters: 'نقشه ستون-خوشه',
      articles: 'تولید مقاله', calendar: 'تقویم محتوا', audit: 'سئوی URL',
      batch: 'سئوی دسته‌جمعی', recommendations: 'توصیه‌های هوش مصنوعی',
      tracking: 'ردیابی کلمات کلیدی', history: 'تاریخچه سئو',
      trends: 'روندهای گوگل', bing: 'سئوی بینگ', technical: 'سئوی فنی', settings: 'تنظیمات'
    }
  };
  document.getElementById('pageTitle').textContent = (titles[lang] || titles.en)[currentPage] || currentPage;
  
  // Update sidebar item texts that don't have data-i18n
  document.querySelectorAll('.nav-item').forEach(item => {
    const page = item.dataset.page;
    if (page) {
      const span = item.querySelector('span[data-i18n]');
      if (span) {
        span.textContent = t(span.dataset.i18n);
      }
    }
  });
  
  // Update theme label
  const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
  document.getElementById('themeLabel').textContent = isDark ? t('lightMode') : t('darkMode');
}

/* ══════════════════════════════════════════════
   State
   ══════════════════════════════════════════════ */
const API = '';
let sessionId = 'sess_' + Math.random().toString(36).substr(2, 9);
let authToken = localStorage.getItem('rankivo_token') || '';
let authUser = localStorage.getItem('rankivo_user') || '';
let currentPage = 'dashboard';
let state = {
  keywordData: null,
  clusterMap: null,
  pipelineResult: null,
  auditResult: null,
  generatedArticle: '',
  articleTopic: '',
  batchCsv: '',
  trendsChart: null,
  trendsRegionChart: null,
};

/* ══════════════════════════════════════════════
   Auth
   ══════════════════════════════════════════════ */
async function doLogin() {
  const username = document.getElementById('loginUsername').value.trim();
  const password = document.getElementById('loginPassword').value;
  if (!username || !password) { showLoginError('Enter username and password'); return; }
  try {
    const res = await fetch(API + '/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    const data = await res.json();
    if (data.success) {
      authToken = data.token;
      authUser = data.username;
      localStorage.setItem('rankivo_token', authToken);
      localStorage.setItem('rankivo_user', authUser);
      hideLoginScreen();
      loadDashboard();
    } else {
      showLoginError(data.error || 'Login failed');
    }
  } catch(e) { showLoginError('Connection failed'); }
}
function showLoginError(msg) {
  const el = document.getElementById('loginError');
  el.textContent = msg;
  el.style.display = 'block';
}
async function doLogout() {
  try { await fetch(API + '/api/auth/logout', { method: 'POST', headers: authHeaders() }); } catch(e) {}
  authToken = '';
  authUser = '';
  localStorage.removeItem('rankivo_token');
  localStorage.removeItem('rankivo_user');
  // Clear cached session data
  localStorage.removeItem('rankivo_kw_data');
  localStorage.removeItem('rankivo_cluster_data');
  // Clear in-memory state
  state.keywordData = null;
  state.clusterMap = null;
  showLoginScreen();
}
function showLoginScreen() {
  const overlay = document.getElementById('loginOverlay');
  overlay.style.display = 'flex';
  document.querySelector('.sidebar').style.display = 'none';
  document.querySelector('.main').style.display = 'none';
}
function hideLoginScreen() {
  const overlay = document.getElementById('loginOverlay');
  overlay.style.display = 'none';
  document.querySelector('.sidebar').style.display = '';
  document.querySelector('.main').style.display = '';
}
function authHeaders() { return authToken ? { 'Authorization': 'Bearer ' + authToken } : {}; }
async function checkAuth() {
  if (!authToken) { showLoginScreen(); return false; }
  try {
    const res = await fetch(API + '/api/auth/check', { headers: authHeaders() });
    const data = await res.json();
    if (data.authenticated) { hideLoginScreen(); return true; }
    showLoginScreen(); return false;
  } catch(e) { showLoginScreen(); return false; }
}

/* ══════════════════════════════════════════════
   Utilities
   ══════════════════════════════════════════════ */
async function api(path, opts = {}) {
  const headers = { 'Content-Type': 'application/json', 'X-Session-ID': sessionId, ...authHeaders(), ...opts.headers };
  const res = await fetch(API + path, { ...opts, headers });
  if (res.status === 401) { showLoginScreen(); return { error: 'Session expired' }; }
  return res.json();
}

function showLoading(text = 'Working...') {
  document.getElementById('loadingText').textContent = text;
  document.getElementById('loadingOverlay').classList.add('active');
}
function hideLoading() { document.getElementById('loadingOverlay').classList.remove('active'); }

function toast(msg, type = 'info') {
  const el = document.createElement('div');
  el.className = 'toast ' + type;
  el.textContent = msg;
  document.getElementById('toastContainer').appendChild(el);
  setTimeout(() => el.remove(), 4000);
}

function escapeHtml(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }

/* ══════════════════════════════════════════════
   Navigation
   ══════════════════════════════════════════════ */
function navigate(page) {
  currentPage = page;
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  const pageEl = document.getElementById('page-' + page);
  const navEl = document.querySelector(`.nav-item[data-page="${page}"]`);
  if (pageEl) pageEl.classList.add('active');
  if (navEl) navEl.classList.add('active');

  const titles = {
    en: {
      dashboard: 'Dashboard', keywords: 'Keyword Research', clusters: 'Pillar-Cluster Map',
      articles: 'Article Generator', calendar: 'Content Calendar', audit: 'SEO Audit',
      batch: 'Batch Audit', recommendations: 'AI Recommendations',
      tracking: 'Keyword Tracking', history: 'Audit History',
      trends: 'Google Trends', bing: 'Bing SEO', 'bing-trends': 'Bing Trends', settings: 'Settings'
    },
    fa: {
      dashboard: 'داشبورد', keywords: 'تحقیق کلمات کلیدی', clusters: 'نقشه ستون-خوشه',
      articles: 'تولید مقاله', calendar: 'تقویم محتوا', audit: 'سئوی URL',
      batch: 'سئوی دسته‌جمعی', recommendations: 'توصیه‌های هوش مصنوعی',
      tracking: 'ردیابی کلمات کلیدی', history: 'تاریخچه سئو',
      trends: 'روندهای گوگل', bing: 'سئوی بینگ', settings: 'تنظیمات'
    }
  };
  document.getElementById('pageTitle').textContent = (titles[currentLanguage] || titles.en)[page] || page;

  // Load page-specific data
  if (page === 'dashboard') loadDashboard();
  if (page === 'history') loadAuditHistory();
  if (page === 'tracking') loadTracking();
  if (page === 'calendar') loadCalendar();
  if (page === 'recommendations') loadRecommendations();
  if (page === 'clusters') updateClusterForm();
  if (page === 'gap') { document.getElementById('gapSeed').focus(); }
  if (page === 'articles') { loadProviders(); showClusterTopicsBtn(); }
  if (page === 'trends') loadTrendsStatus();
  if (page === 'bing-trends') loadBingTrendsStatus();
  if (page === 'settings') { loadUsers(); loadSettings(); }

  // Close mobile sidebar
  document.getElementById('sidebar').classList.remove('open');
}

/* ══════════════════════════════════════════════
   Theme
   ══════════════════════════════════════════════ */
function toggleTheme() {
  const html = document.documentElement;
  const isDark = html.getAttribute('data-theme') === 'dark';
  html.setAttribute('data-theme', isDark ? 'light' : 'dark');
  document.getElementById('themeIcon').className = isDark ? 'fas fa-moon' : 'fas fa-sun';
  document.getElementById('themeLabel').textContent = isDark ? t('lightMode') : t('darkMode');
  localStorage.setItem('theme', isDark ? 'light' : 'dark');
}
(function() {
  const saved = localStorage.getItem('theme');
  if (saved === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
    document.getElementById('themeIcon').className = 'fas fa-sun';
    document.getElementById('themeLabel').textContent = 'Light Mode';
  }
})();

/* ══════════════════════════════════════════════
   Dashboard
   ══════════════════════════════════════════════ */
async function loadDashboard() {
  try {
    const status = await api('/api/status');
    document.getElementById('dbStatus').textContent = status.database;
    document.getElementById('aiStatus').textContent = status.providers.length ? status.providers.join(', ') : 'None';
    document.getElementById('defaultAi').textContent = status.default_provider;

    const badge = document.getElementById('statusBadge');
    badge.className = 'status-badge ' + (status.providers.length ? 'online' : 'offline');
    document.getElementById('statusText').textContent = status.providers.length ? t('connected') : t('noAi');

    // Audit history chart
    const hist = await api('/api/audit-history?limit=20');
    if (hist.history && hist.history.length) {
      document.getElementById('dashAuditCount').textContent = hist.history.length;
      document.getElementById('dashHistoryEmpty').style.display = 'none';
      document.getElementById('dashPageTypeEmpty').style.display = 'none';
      renderDashHistoryChart(hist.history);
      renderDashPageTypeChart(hist.history);
    } else {
      document.getElementById('dashHistoryEmpty').style.display = 'block';
      document.getElementById('dashPageTypeEmpty').style.display = 'block';
      document.getElementById('dashAuditCount').textContent = '0';
    }

    // Calendar count
    const cal = await api('/api/calendar');
    document.getElementById('dashCalCount').textContent = cal.events ? cal.events.length : '0';

    // Keyword/cluster from session
    if (state.keywordData) {
      const allKw = new Set();
      ['suggestions','modifier_expanded','related_searches','people_also_ask'].forEach(k => {
        (state.keywordData[k] || []).forEach(w => allKw.add(w));
      });
      document.getElementById('dashKwCount').textContent = allKw.size;
    }
    if (state.clusterMap) {
      document.getElementById('dashClusterCount').textContent = state.clusterMap.stats.total_clusters;
    }
  } catch(e) { console.error('Dashboard load error:', e); }

  // Load LLM status
  try {
    const llmRes = await api('/api/llm-intel/status');
    const ollamaEl = document.getElementById('llmOllamaStatus');
    const embedEl = document.getElementById('llmEmbedModel');
    const capsEl = document.getElementById('llmCapabilities');
    if (llmRes.ollama_running) {
      ollamaEl.className = 'badge badge-success';
      ollamaEl.textContent = 'Connected';
    } else {
      ollamaEl.className = 'badge badge-danger';
      ollamaEl.textContent = 'Offline';
    }
    embedEl.textContent = llmRes.has_embedding_model ? 'nomic-embed-text' : 'TF-IDF fallback';
    const caps = llmRes.capabilities || {};
    let capsHtml = '';
    if (caps.intent_classification) capsHtml += '<span class="badge badge-success" style="font-size:0.7rem;"><i class="fas fa-check"></i> Intent</span>';
    else capsHtml += '<span class="badge badge-danger" style="font-size:0.7rem;"><i class="fas fa-times"></i> Intent</span>';
    if (caps.semantic_clustering) capsHtml += '<span class="badge badge-success" style="font-size:0.7rem;"><i class="fas fa-check"></i> Clustering</span>';
    else capsHtml += '<span class="badge badge-warning" style="font-size:0.7rem;"><i class="fas fa-exclamation"></i> Clustering</span>';
    if (caps.difficulty_estimation) capsHtml += '<span class="badge badge-success" style="font-size:0.7rem;"><i class="fas fa-check"></i> Difficulty</span>';
    else capsHtml += '<span class="badge badge-danger" style="font-size:0.7rem;"><i class="fas fa-times"></i> Difficulty</span>';
    capsEl.innerHTML = capsHtml;
  } catch(e) { console.log('LLM status load error:', e); }
}

let dashChart = null;
let dashPageTypeChart = null;
function renderDashPageTypeChart(history) {
  const ctx = document.getElementById('dashPageTypeChart');
  if (dashPageTypeChart) dashPageTypeChart.destroy();
  const counts = {};
  history.forEach(h => {
    const pt = h.page_type || 'generic';
    counts[pt] = (counts[pt] || 0) + 1;
  });
  const labels = Object.keys(counts);
  const colors = { homepage: '#6366f1', product: '#10b981', blog: '#f59e0b', generic: '#94a3b8' };
  const bgColors = labels.map(l => colors[l] || '#64748b');
  dashPageTypeChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels.map(l => l.charAt(0).toUpperCase() + l.slice(1)),
      datasets: [{
        data: Object.values(counts),
        backgroundColor: bgColors,
        borderWidth: 0,
        hoverOffset: 6,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      cutout: '60%',
      plugins: {
        legend: { position: 'bottom', labels: { padding: 14, usePointStyle: true, pointStyleWidth: 10, font: { size: 12 } } },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${ctx.label}: ${ctx.raw} audit${ctx.raw !== 1 ? 's' : ''}`
          }
        }
      }
    }
  });
}
function renderDashHistoryChart(history) {
  const ctx = document.getElementById('dashHistoryChart');
  if (dashChart) dashChart.destroy();
  const labels = history.slice(0, 10).reverse().map(h => { try { return new URL(h.url).hostname; } catch { return h.url.substring(0,20); } });
  const scores = history.slice(0, 10).reverse().map(h => h.score);
  dashChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'SEO Score',
        data: scores,
        backgroundColor: scores.map(s => s >= 80 ? '#10b981' : s >= 50 ? '#f59e0b' : '#ef4444'),
        borderRadius: 6,
        barPercentage: 0.6,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, max: 100, grid: { color: 'rgba(0,0,0,0.06)' } },
        x: { grid: { display: false }, ticks: { maxRotation: 45 } }
      }
    }
  });
}

/* ══════════════════════════════════════════════
   Keyword Research
   ══════════════════════════════════════════════ */
// ──────────────────────────────────────────────
// LLM Keyword Intelligence Functions
// ──────────────────────────────────────────────
async function runLlmIntelligence(keywords, seed) {
  // Show progress indicator
  var progressEl = document.createElement('div');
  progressEl.id = 'llmProgress';
  progressEl.style.cssText = 'position:fixed;bottom:24px;right:24px;z-index:9999;padding:12px 20px;background:var(--bg-card);border:1px solid var(--accent);border-radius:var(--radius);box-shadow:0 4px 12px rgba(0,0,0,0.15);font-size:0.88rem;display:flex;align-items:center;gap:10px;animation:fadeIn 0.3s ease;';
  progressEl.innerHTML = '<span class="spinner" style="width:16px;height:16px;border-width:2px;"></span><span id="llmProgressText">Analyzing keywords with AI...</span>';
  document.body.appendChild(progressEl);

  var progressSteps = ['Classifying intent...', 'Building clusters...', 'Estimating difficulty...'];
  var stepIdx = 0;
  var progressInterval = setInterval(function() {
    var el = document.getElementById('llmProgressText');
    if (el && stepIdx < progressSteps.length) {
      el.textContent = progressSteps[stepIdx++];
    } else {
      clearInterval(progressInterval);
    }
  }, 8000);

  try {
    const res = await fetch(API + '/api/llm-intel/analyze', {
      method: 'POST',
      headers: { ...authHeaders(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ keywords, seed, classify_intent: true, cluster: true, estimate_difficulty: true, difficulty_sample_size: 3 })
    });
    clearInterval(progressInterval);
    var progEl = document.getElementById('llmProgress');
    if (progEl) progEl.remove();
    if (!res.ok) return null;
    return await res.json();
  } catch(e) {
    clearInterval(progressInterval);
    var progEl = document.getElementById('llmProgress');
    if (progEl) progEl.remove();
    console.log('LLM intel error:', e);
    toast('LLM analysis unavailable - using fallback.', 'error');
    return null;
  }
}

function renderKeywordDifficulty(difficulties) {
  if (!difficulties || Object.keys(difficulties).length === 0) return;
  const card = document.getElementById('kwDifficultyCard');
  if (!card) return;
  card.style.display = 'block';
  
  let html = '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px;">';
  for (const [kw, data] of Object.entries(difficulties)) {
    const score = data.score || 0;
    const level = data.level || 'medium';
    const color = score <= 30 ? 'var(--success)' : score <= 60 ? 'var(--warning)' : 'var(--danger)';
    const bgColor = score <= 30 ? 'var(--success-bg)' : score <= 60 ? 'var(--warning-bg)' : 'var(--danger-bg)';
    const levelLabel = level.replace('_', ' ');
    
    html += '<div style="padding:12px;border-radius:var(--radius);border:1px solid var(--border);background:var(--bg-card);">';
    html += '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">';
    html += '<span style="font-weight:600;font-size:0.9rem;">' + kw + '</span>';
    html += '<span style="background:' + bgColor + ';color:' + color + ';padding:2px 8px;border-radius:12px;font-size:0.75rem;font-weight:600;">' + levelLabel + '</span>';
    html += '</div>';
    html += '<div style="background:var(--bg-input);border-radius:4px;height:6px;margin-bottom:8px;"><div style="background:' + color + ';height:100%;width:' + score + '%;border-radius:4px;transition:width 0.3s;"></div></div>';
    html += '<div style="font-size:0.78rem;color:var(--text-muted);">Score: ' + score + '/100</div>';
    if (data.recommendation) {
      html += '<div style="font-size:0.78rem;color:var(--text-secondary);margin-top:4px;font-style:italic;">' + data.recommendation + '</div>';
    }
    html += '</div>';
  }
  html += '</div>';
  document.getElementById('kwDifficultyContent').innerHTML = html;
  
  // Update badge
  const scores = Object.values(difficulties).map(d => d.score || 0);
  const avg = Math.round(scores.reduce((a,b) => a+b, 0) / scores.length);
  const badge = document.getElementById('kwDifficultyBadge');
  if (badge) badge.textContent = 'Avg: ' + avg + '/100';
}

function renderIntentBadges(intentMap) {
  if (!intentMap) return;
  // Update existing intent badges with LLM-sourced data
  const el = document.getElementById('kwSuggestions');
  if (!el) return;
  // The intent chart will be re-rendered by the caller
}

async function runKeywordResearch() {
  const seed = document.getElementById('kwSeed').value.trim();
  if (!seed) { toast('Enter a seed keyword', 'error'); return; }

  // Check if auto-pipeline is enabled
  if (document.getElementById('kwAutoPipeline').checked) {
    var depth = parseInt(document.getElementById('kwDepth').value);
    var expand = document.getElementById('kwExpand').checked;
    await runAutoPipeline(seed, depth, expand);
    return;
  }

  showLoading('Researching keywords...');
  document.getElementById('btnResearch').disabled = true;
  try {
    const data = await api('/api/keyword-research', {
      method: 'POST',
      body: JSON.stringify({
        seed,
        depth: parseInt(document.getElementById('kwDepth').value),
        expand_modifiers: document.getElementById('kwExpand').checked
      })
    });
    hideLoading();

    if (data.error) { toast(data.error, 'error'); return; }

    state.keywordData = data;
    try { localStorage.setItem('rankivo_kw_data', JSON.stringify(data)); } catch(e) {}
    document.getElementById('kwResults').style.display = 'block';
    document.getElementById('btnTrackKw').style.display = 'inline-flex';
    document.getElementById('btnExportCsv').style.display = 'inline-flex';

    // Compute totals
    const allKw = new Set();
    ['suggestions','modifier_expanded','related_searches','people_also_ask'].forEach(k => {
      (data[k] || []).forEach(w => allKw.add(w));
    });

    // Metrics
    document.getElementById('kwMetrics').innerHTML = `
      <div class="metric-card"><div class="metric-icon purple"><i class="fas fa-key"></i></div><div class="metric-label">Total Keywords</div><div class="metric-value">${allKw.size}</div></div>
      <div class="metric-card"><div class="metric-icon blue"><i class="fas fa-lightbulb"></i></div><div class="metric-label">Autocomplete</div><div class="metric-value">${(data.suggestions||[]).length}</div></div>
      <div class="metric-card"><div class="metric-icon green"><i class="fas fa-question-circle"></i></div><div class="metric-label">People Also Ask</div><div class="metric-value">${(data.people_also_ask||[]).length}</div></div>
      <div class="metric-card"><div class="metric-icon yellow"><i class="fas fa-link"></i></div><div class="metric-label">Related Searches</div><div class="metric-value">${(data.related_searches||[]).length}</div></div>
    `;

    // Intent chart
    renderIntentChart(data.intent_map || {});

    // Suggestions
    document.getElementById('kwSuggestions').innerHTML = (data.suggestions||[]).map(k =>
      `<div style="padding:6px 0;border-bottom:1px solid var(--border);font-size:0.88rem;">${escapeHtml(k)}</div>`
    ).join('') || '<div class="empty-state" style="padding:16px;"><p>No suggestions found.</p></div>';

    // PAA
    document.getElementById('kwPAA').innerHTML = (data.people_also_ask||[]).map(q =>
      `<div class="issue-item info"><span class="issue-icon">❓</span><div>${escapeHtml(q)}</div></div>`
    ).join('') || '<div class="empty-state" style="padding:16px;"><p>No PAA questions found.</p></div>';

    // Related
    document.getElementById('kwRelated').innerHTML = (data.related_searches||[]).map(r =>
      `<span class="badge badge-info" style="margin:3px;">${escapeHtml(r)}</span>`
    ).join('') || '<div class="empty-state" style="padding:16px;"><p>No related searches found.</p></div>';

    // SERP
    if (data.serp_results && data.serp_results.length) {
      document.getElementById('kwSerpTable').innerHTML = `
        <table>
          <thead><tr><th>Title</th><th>URL</th><th>Snippet</th></tr></thead>
          <tbody>${data.serp_results.map(r => `<tr><td style="max-width:300px;">${escapeHtml(r.title||'')}</td><td style="max-width:250px;font-size:0.8rem;color:var(--accent);">${escapeHtml(r.url||'')}</td><td style="max-width:400px;font-size:0.8rem;">${escapeHtml((r.snippet||'').substring(0,150))}</td></tr>`).join('')}</tbody>
        </table>`;
    }

    // Render Google Trends mini-chart if available
    if (data.trends && data.trends.dates && data.trends.dates.length) {
      renderKwTrendsChart(data.trends, data.seed);
      if (data.trends_related) {
        renderKwTrendsRelated(data.trends_related);
      }
      document.getElementById('kwTrendsCard').style.display = 'block';
    }

    // Run LLM Intelligence if enabled
    if (document.getElementById('kwUseLlm').checked) {
      document.getElementById('btnResearch').innerHTML = '<span class="spinner"></span> LLM Analysis...';
      try {
        const allKwList = [...allKw];
        const llmData = await runLlmIntelligence(allKwList, seed);
        if (llmData) {
          // Merge LLM intent classification into intent_map
          if (llmData.intents && Object.keys(llmData.intents).length > 0) {
            if (!data.intent_map) data.intent_map = {};
            Object.assign(data.intent_map, llmData.intents);
            // Re-render the intent chart with LLM-enhanced data
            if (data.intent_map && Object.keys(data.intent_map).length > 0) renderIntentChart(data.intent_map);
          }
          // Render keyword difficulty
          if (llmData.difficulties) {
            renderKeywordDifficulty(llmData.difficulties);
          }
          // Show cluster method info
          if (llmData.clusters) {
            const clusterCount = llmData.clusters.num_clusters || 0;
            toast('LLM clustering: ' + clusterCount + ' semantic clusters found', 'info');
          }
          toast('LLM intelligence analysis complete!', 'success');
        }
      } catch(llmErr) {
        console.log('LLM intelligence error:', llmErr);
        toast('LLM analysis failed - using heuristic results', 'error');
      }
      document.getElementById('btnResearch').innerHTML = '<i class="fas fa-rocket"></i> ' + t('startResearch');
    }

    toast('Keyword research complete!', 'success');
  } catch(e) {
    hideLoading();
    toast('Research failed: ' + e.message, 'error');
  }
  document.getElementById('btnResearch').disabled = false;
}

let kwIntentChart = null;
function renderIntentChart(intentMap) {
  const counts = {};
  Object.values(intentMap).forEach(i => { counts[i] = (counts[i]||0)+1; });
  const ctx = document.getElementById('kwIntentChart');
  if (kwIntentChart) kwIntentChart.destroy();
  const colors = { informational: '#3b82f6', commercial: '#f59e0b', transactional: '#10b981', navigational: '#8b5cf6' };
  kwIntentChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: Object.keys(counts),
      datasets: [{ data: Object.values(counts), backgroundColor: Object.keys(counts).map(k => colors[k] || '#94a3b8'), borderWidth: 0 }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'right', labels: { padding: 16, usePointStyle: true } } },
      cutout: '60%'
    }
  });
}

/* ══════════════════════════════════════════════
   Keyword Research — Integrated Trends
   ══════════════════════════════════════════════ */
let kwTrendsChartInstance = null;

function renderKwTrendsChart(trendsData, seed) {
  const ctx = document.getElementById('kwTrendsChart');
  if (kwTrendsChartInstance) kwTrendsChartInstance.destroy();
  
  document.getElementById('kwTrendsSeed').textContent = seed;
  
  const dates = trendsData.dates || [];
  const values = (trendsData.values || {})[seed] || [];
  
  if (!dates.length || !values.length) {
    document.getElementById('kwTrendsStatus').textContent = 'No data';
    document.getElementById('kwTrendsCard').style.display = 'none';
    return;
  }
  
  document.getElementById('kwTrendsStatus').textContent = '12-month trend';
  
  // Only show every ~30th date label to avoid crowding
  const labelInterval = Math.max(1, Math.floor(dates.length / 12));
  
  kwTrendsChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: dates,
      datasets: [{
        label: seed,
        data: values,
        borderColor: '#6366f1',
        backgroundColor: 'rgba(99,102,241,0.12)',
        fill: true,
        tension: 0.4,
        pointRadius: 2,
        pointHoverRadius: 5,
        borderWidth: 2,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            title: (items) => items[0].label,
            label: (ctx) => ` Interest: ${ctx.raw}`
          }
        }
      },
      scales: {
        y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' }, ticks: { maxTicksLimit: 5 } },
        x: { 
          grid: { display: false }, 
          ticks: { 
            maxTicksLimit: 8,
            callback: function(val, idx) {
              return idx % labelInterval === 0 ? this.getLabelForValue(val).substring(5, 10) : '';
            }
          }
        }
      },
      interaction: { mode: 'index', intersect: false }
    }
  });
}

function renderKwTrendsRelated(relatedData) {
  const container = document.getElementById('kwTrendsRelated');
  let html = '';
  
  for (const [kw, related] of Object.entries(relatedData)) {
    const topQueries = (related.top || []).slice(0, 5);
    if (topQueries.length) {
      html += `<div style="margin-top:8px;">
        <div style="font-size:0.8rem;font-weight:600;color:var(--text-muted);margin-bottom:4px;">Related trending queries:</div>
        ${topQueries.map(q => `<span class="trend-chip" style="font-size:0.78rem;margin:2px;">${escapeHtml(q.query || q.value || '')}</span>`).join('')}
      </div>`;
    }
  }
  
  container.innerHTML = html;
}

async function trackCurrentKeyword() {
  if (!state.keywordData) { toast('No keyword data to track', 'error'); return; }
  showLoading('Tracking keyword...');
  const res = await api('/api/tracking', { method: 'POST', body: '{}' });
  hideLoading();
  if (res.success) toast(`Tracking "${res.keyword}"!`, 'success');
  else toast(res.error || 'Failed', 'error');
}

/* ══════════════════════════════════════════════
   Pillar-Cluster
   ══════════════════════════════════════════════ */
function updateClusterForm() {
  var wasFromCache = false;
  // Try to restore keyword data from localStorage if not in memory
  if (!state.keywordData) {
    try {
      var saved = localStorage.getItem('rankivo_kw_data');
      if (saved) { state.keywordData = JSON.parse(saved); wasFromCache = true; }
    } catch(e) { console.warn('localStorage read error:', e); }
  }
  if (!state.clusterMap) {
    try {
      var savedCluster = localStorage.getItem('rankivo_cluster_data');
      if (savedCluster) { state.clusterMap = JSON.parse(savedCluster); wasFromCache = true; }
    } catch(e) { console.warn('localStorage read error:', e); }
  }
  document.getElementById('clusterNoData').style.display = state.keywordData ? 'none' : 'block';
  document.getElementById('clusterForm').style.display = state.keywordData ? 'block' : 'none';

  // Show cached data indicator
  var cacheIndicator = document.getElementById('clusterCacheIndicator');
  if (state.keywordData && wasFromCache) {
    if (!cacheIndicator) {
      cacheIndicator = document.createElement('div');
      cacheIndicator.id = 'clusterCacheIndicator';
      cacheIndicator.style.cssText = 'padding:8px 16px;margin-bottom:12px;background:var(--warning-bg);border:1px solid var(--warning);border-radius:var(--radius);font-size:0.85rem;display:flex;align-items:center;justify-content:space-between;';
      cacheIndicator.innerHTML = '<span><i class="fas fa-database" style="margin-right:8px;color:var(--warning);"></i><span data-i18n="cachedData">Restored from local cache</span></span><button class="btn btn-sm btn-secondary" onclick="refreshClusterData()"><i class="fas fa-sync-alt"></i> <span data-i18n="refresh">Refresh</span></button>';
      if (typeof setLanguage === 'function' && currentLanguage) setLanguage(currentLanguage);
      var form = document.getElementById('clusterForm');
      if (form) form.parentNode.insertBefore(cacheIndicator, form);
    }
    cacheIndicator.style.display = 'flex';
  } else if (cacheIndicator) {
    cacheIndicator.style.display = 'none';
  }
}

function refreshClusterData() {
  // Clear cached data and navigate to keyword research
  localStorage.removeItem('rankivo_kw_data');
  localStorage.removeItem('rankivo_cluster_data');
  state.keywordData = null;
  state.clusterMap = null;
  var cacheIndicator = document.getElementById('clusterCacheIndicator');
  if (cacheIndicator) cacheIndicator.style.display = 'none';
  navigate('keywords');
}

async function buildClusterMap() {
  showLoading('Building cluster map...');
  document.getElementById('btnBuildCluster').disabled = true;
  try {
    const data = await api('/api/pillar-cluster', {
      method: 'POST',
      body: JSON.stringify({ threshold: parseFloat(document.getElementById('clusterThreshold').value) })
    });
    hideLoading();
    if (data.error) { toast(data.error, 'error'); return; }

    // Use semantic LLM clustering if enabled
    if (document.getElementById('useSemanticClustering').checked) {
      document.getElementById('btnBuildCluster').innerHTML = '<span class="spinner"></span> Semantic Clustering...';
      try {
        const kwData = state.keywordData || {};
        const allKw = new Set();
        ['suggestions','modifier_expanded','related_searches','people_also_ask'].forEach(k => {
          (kwData[k] || []).forEach(w => allKw.add(w));
        });
        const keywords = [...allKw].slice(0, 100);
        const seed = kwData.seed || '';
        const llmRes = await fetch(API + '/api/llm-intel/cluster', {
          method: 'POST',
          headers: { ...authHeaders(), 'Content-Type': 'application/json' },
          body: JSON.stringify({ keywords, seed })
        });
        if (llmRes.ok) {
          const llmCluster = await llmRes.json();
          if (!llmCluster.error && llmCluster.clusters) {
            // Convert LLM clusters back to pillar-cluster format
            const pillarClusters = [];
            const contentPlan = [];
            (llmCluster.clusters.clusters || []).forEach((cluster, idx) => {
              const kwList = cluster.keywords || [];
              const pillarKw = kwList[0] || ('Cluster ' + (idx + 1));
              const intent = (data.intent_map || {})[pillarKw] || 'informational';
              pillarClusters.push({
                pillar_keyword: pillarKw,
                pillar_title: pillarKw,
                keywords: kwList,
                keyword_count: kwList.length,
              });
              const articles = kwList.slice(0, 5).map(kw => ({
                keyword: kw,
                intent: (data.intent_map || {})[kw] || 'informational',
                suggested_title: kw,
              }));
              contentPlan.push({
                pillar_keyword: pillarKw,
                pillar_title: pillarKw,
                pillar_intent: intent,
                articles,
                total_content_pieces: articles.length,
              });
            });
            data.pillar_clusters = pillarClusters;
            data.content_plan = contentPlan;
            data.stats = {
              total_clusters: pillarClusters.length,
              total_keywords: keywords.length,
              total_content_pieces: contentPlan.reduce((sum, p) => sum + p.articles.length, 0),
            };
            toast('Semantic clustering applied: ' + pillarClusters.length + ' clusters', 'success');
          }
        }
      } catch(semErr) {
        console.log('Semantic clustering error:', semErr);
        toast('Semantic clustering failed - using word-overlap clustering', 'error');
      }
      document.getElementById('btnBuildCluster').innerHTML = '<i class="fas fa-project-diagram"></i> ' + t('buildMap');
    }

    state.clusterMap = data;
    try { localStorage.setItem('rankivo_cluster_data', JSON.stringify(data)); } catch(e) {}
    document.getElementById('clusterResults').style.display = 'block';

    // Metrics
    const s = data.stats;
    document.getElementById('clusterMetrics').innerHTML = `
      <div class="metric-card"><div class="metric-icon purple"><i class="fas fa-layer-group"></i></div><div class="metric-label">Clusters</div><div class="metric-value">${s.total_clusters}</div></div>
      <div class="metric-card"><div class="metric-icon blue"><i class="fas fa-key"></i></div><div class="metric-label">Keywords</div><div class="metric-value">${s.total_keywords}</div></div>
      <div class="metric-card"><div class="metric-icon green"><i class="fas fa-file-alt"></i></div><div class="metric-label">Content Pieces</div><div class="metric-value">${s.total_content_pieces}</div></div>
    `;

    // Chart
    renderClusterChart(data.pillar_clusters);

    // Content plan
    let html = '';
    data.content_plan.forEach((plan, i) => {
      html += `
        <div class="expander">
          <div class="expander-header" onclick="toggleExpander(this)">
            <span>🏛️ ${escapeHtml(plan.pillar_title)} (${plan.total_content_pieces} articles)</span>
            <i class="fas fa-chevron-right chevron"></i>
          </div>
          <div class="expander-body">
            <div style="margin-bottom:8px;"><strong>Pillar keyword:</strong> ${escapeHtml(plan.pillar_keyword)}</div>
            <div style="margin-bottom:8px;"><strong>Intent:</strong> <span class="badge badge-purple">${plan.pillar_intent}</span></div>
            <strong>Articles:</strong>
            <table style="margin-top:8px;">
              <thead><tr><th>Keyword</th><th>Intent</th><th>Suggested Title</th></tr></thead>
              <tbody>${plan.articles.map(a => `<tr><td>${escapeHtml(a.keyword)}</td><td><span class="badge badge-info">${a.intent}</span></td><td>${escapeHtml(a.suggested_title)}</td></tr>`).join('')}</tbody>
            </table>
          </div>
        </div>`;
    });
    if (data.trends && data.trends.dates && data.trends.dates.length) {
      renderClusterTrendsChart(data.trends, data.seed || (state.keywordData ? state.keywordData.seed : ''));
    }
    document.getElementById('clusterContentPlan').innerHTML = html;
    toast('Cluster map built!', 'success');
  } catch(e) { hideLoading(); toast('Failed: ' + e.message, 'error'); }
  document.getElementById('btnBuildCluster').disabled = false;
}

let clusterChart = null;
let clusterTrendsChartInstance = null;

function renderClusterTrendsChart(trendsData, seed) {
  var cardEl = document.getElementById('clusterTrendsCard');
  if (cardEl) cardEl.style.display = 'block';
  var ctx = document.getElementById('clusterTrendsChart');
  if (clusterTrendsChartInstance) clusterTrendsChartInstance.destroy();
  var dates = trendsData.dates || [];
  var vals = (trendsData.values || {})[seed] || [];
  if (!dates.length || !vals.length) {
    if (cardEl) cardEl.style.display = 'none';
    return;
  }
  clusterTrendsChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: dates,
      datasets: [{ label: seed || 'Trend', data: vals, borderColor: '#6366f1', backgroundColor: 'rgba(99,102,241,0.12)', fill: true, tension: 0.4, pointRadius: 2, pointHoverRadius: 5, borderWidth: 2 }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: { y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' }, ticks: { maxTicksLimit: 5 } }, x: { grid: { display: false }, ticks: { maxTicksLimit: 8 } } },
      interaction: { mode: 'index', intersect: false }
    }
  });
}


function renderClusterChart(pillarClusters) {
  const ctx = document.getElementById('clusterChart');
  if (clusterChart) clusterChart.destroy();
  const labels = pillarClusters.map(pc => pc.pillar_keyword.substring(0, 25));
  const sizes = pillarClusters.map(pc => pc.size);
  clusterChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Keywords',
        data: sizes,
        backgroundColor: 'rgba(99,102,241,0.7)',
        borderColor: 'rgba(99,102,241,1)',
        borderWidth: 1,
        borderRadius: 6,
        barPercentage: 0.6,
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.06)' } },
        y: { grid: { display: false } }
      }
    }
  });
}

function toggleExpander(header) {
  header.classList.toggle('open');
  header.nextElementSibling.classList.toggle('open');
}

/* ══════════════════════════════════════════════
   Article Generator
   ══════════════════════════════════════════════ */


function renderClusterFromState() {
  if (!state.clusterMap) return;
  var cm = state.clusterMap;
  document.getElementById('clusterResults').style.display = 'block';
  document.getElementById('clusterMetrics').innerHTML = '<div class="metric-card"><div class="metric-icon purple"><i class="fas fa-key"></i></div><div class="metric-label">Total Keywords</div><div class="metric-value">' + cm.stats.total_keywords + '</div></div><div class="metric-card"><div class="metric-icon blue"><i class="fas fa-layer-group"></i></div><div class="metric-label">Clusters</div><div class="metric-value">' + cm.stats.total_clusters + '</div></div><div class="metric-card"><div class="metric-icon green"><i class="fas fa-file-alt"></i></div><div class="metric-label">Content Pieces</div><div class="metric-value">' + cm.stats.total_content_pieces + '</div></div><div class="metric-card"><div class="metric-icon yellow"><i class="fas fa-chart-pie"></i></div><div class="metric-label">Clusters</div><div class="metric-value">' + cm.stats.total_clusters + '</div></div>';
  renderClusterChart(cm.pillar_clusters);
  renderClusterContentPlan(cm.content_plan);
  // Show trends if available
  if (cm.trends && cm.trends.dates && cm.trends.dates.length) {
    renderClusterTrendsChart(cm.trends, cm.seed);
  }
}

function showClusterTopicsBtn() {
  var btn = document.getElementById('btnLoadClusterTopics');
  if (btn) {
    btn.style.display = (state.clusterMap && state.clusterMap.content_plan && state.clusterMap.content_plan.length) ? 'inline-flex' : 'none';
  }
}


// ══════════════════════════════════════════════
// Cluster Article Selector & Batch Generation
// ══════════════════════════════════════════════

function openClusterSelector() {
  if (!state.clusterMap || !state.clusterMap.content_plan || !state.clusterMap.content_plan.length) {
    toast('No cluster data available. Run the pipeline or build a cluster map first.', 'error');
    return;
  }
  
  var plan = state.clusterMap.content_plan;
  var listEl = document.getElementById('clusterSelectorList');
  var emptyEl = document.getElementById('clusterSelectorEmpty');
  
  if (!plan.length) {
    listEl.innerHTML = '';
    emptyEl.style.display = 'block';
    document.getElementById('btnGenerateSelected').disabled = true;
    document.getElementById('modalOverlay').classList.add('active');
    return;
  }
  
  emptyEl.style.display = 'none';
  var html = '';
  var allSelected = true;
  
  for (var i = 0; i < plan.length; i++) {
    var cluster = plan[i];
    var pillarTitle = cluster.pillar_title || cluster.pillar_keyword || 'Pillar ' + (i + 1);
    var keywords = cluster.keywords || cluster.articles || [];
    var kwText = '';
    if (Array.isArray(keywords)) {
      kwText = keywords.slice(0, 8).map(function(k) {
        return typeof k === 'string' ? k : (k.keyword || k.suggested_title || '');
      }).filter(Boolean).join(', ');
    }
    
    // Determine priority badge
    var priority = cluster.priority || 'medium';
    var priorityLabel = priority.charAt(0).toUpperCase() + priority.slice(1);
    
    html += '<label class="cluster-select-item selected" data-index="' + i + '">';
    html += '  <input type="checkbox" class="cluster-checkbox" data-index="' + i + '" checked onchange="updateClusterSelection()">';
    html += '  <div class="item-content">';
    html += '    <div class="item-title">' + escapeHtml(pillarTitle) + '</div>';
    html += '    <div class="item-keywords">' + escapeHtml(kwText.substring(0, 120)) + '</div>';
    html += '  </div>';
    html += '  <div class="item-meta">';
    html += '    <span class="priority-badge ' + priority + '">' + priorityLabel + '</span>';
    html += '  </div>';
    html += '</label>';
  }
  
  listEl.innerHTML = html;
  document.getElementById('btnSelectAllCluster').innerHTML = '<i class="fas fa-check-square"></i> ' + t('deselectAll') || 'Deselect All';
  document.getElementById('btnSelectAllCluster').dataset.all = 'true';
  updateClusterSelection();
  document.getElementById('clusterSelectorModal').classList.add('active');
}

function closeClusterSelector() {
  document.getElementById('clusterSelectorModal').classList.remove('active');
}

function updateClusterSelection() {
  var checked = document.querySelectorAll('.cluster-checkbox:checked').length;
  var total = document.querySelectorAll('.cluster-checkbox').length;
  document.getElementById('clusterSelectedCount').textContent = checked + ' / ' + total + ' ' + t('selected');
  document.getElementById('btnGenerateSelected').disabled = checked === 0;
  
  // Update visual state
  document.querySelectorAll('.cluster-select-item').forEach(function(item) {
    var cb = item.querySelector('.cluster-checkbox');
    item.classList.toggle('selected', cb && cb.checked);
  });
  
  // Update select-all button text
  var allChecked = checked === total;
  var btn = document.getElementById('btnSelectAllCluster');
  if (btn) {
    btn.innerHTML = allChecked
      ? '<i class="fas fa-check-square"></i> ' + (t('deselectAll') || 'Deselect All')
      : '<i class="fas fa-square"></i> ' + (t('selectAll') || 'Select All');
    btn.dataset.all = allChecked ? 'true' : 'false';
  }
}

function toggleSelectAllCluster() {
  var allChecked = document.getElementById('btnSelectAllCluster').dataset.all === 'true';
  document.querySelectorAll('.cluster-checkbox').forEach(function(cb) {
    cb.checked = !allChecked;
  });
  updateClusterSelection();
}

async function generateSelectedArticles() {
  var checked = document.querySelectorAll('.cluster-checkbox:checked');
  if (!checked.length) { toast('Select at least one article to generate.', 'error'); return; }
  
  var plan = state.clusterMap.content_plan;
  var provider = document.getElementById('articleProvider').value;
  var language = document.getElementById('articleLanguage').value;
  var wordCount = parseInt(document.getElementById('articleWordCount').value) || 1500;
  var tone = document.getElementById('articleTone').value;
  var style = document.getElementById('articleStyle').value;
  
  var articles = [];
  checked.forEach(function(cb) {
    var idx = parseInt(cb.dataset.index);
    var cluster = plan[idx];
    if (!cluster) return;
    var keywords = cluster.keywords || cluster.articles || [];
    var kwList = keywords.map(function(k) {
      return typeof k === 'string' ? k : (k.keyword || k.suggested_title || '');
    }).filter(Boolean);
    articles.push({
      topic: cluster.pillar_title || cluster.pillar_keyword,
      keywords: kwList,
      provider: provider,
      language: language,
      word_count: wordCount,
      tone: tone,
      style: style,
    });
  });
  
  if (!articles.length) { toast('No valid article definitions.', 'error'); return; }
  
  // Show progress
  closeClusterSelector();
  showLoading('Generating ' + articles.length + ' article(s)...');
  document.getElementById('batchArticleResults').style.display = 'block';
  document.getElementById('batchArticleList').innerHTML = '<div class="batch-progress"><div class="progress-bar"><div class="progress-fill" style="width:0%"></div></div><span id="batchProgressText">0 / ' + articles.length + '</span></div>';
  
  // Call batch API
  var data = await api('/api/article/generate-batch', {
    method: 'POST',
    body: JSON.stringify({ articles: articles, provider: provider, language: language })
  });
  
  hideLoading();
  
  if (data.error) {
    toast('Batch generation failed: ' + data.error, 'error');
    document.getElementById('batchArticleResults').style.display = 'none';
    return;
  }
  
  toast('Generated ' + data.successful + ' / ' + data.total + ' articles', data.failed > 0 ? 'warning' : 'success');
  
  // Render results
  renderBatchResults(data.results, articles);
}

function renderBatchResults(results, articleDefs) {
  var listEl = document.getElementById('batchArticleList');
  if (!results || !results.length) {
    listEl.innerHTML = '<div class="empty-state" style="padding:24px;"><i class="fas fa-file-alt"></i><p>No articles were generated.</p></div>';
    return;
  }
  
  var html = '';
  for (var i = 0; i < results.length; i++) {
    var r = results[i];
    var success = r.success;
    var topic = r.topic || 'Article ' + (i + 1);
    var icon = success ? '<i class="fas fa-check-circle status-icon success"></i>' : '<i class="fas fa-exclamation-circle status-icon error"></i>';
    var preview = '';
    if (success && r.article) {
      // Get first line as preview
      var lines = r.article.split('\n').filter(Boolean);
      preview = lines[0] || topic;
      if (preview.length > 60) preview = preview.substring(0, 60) + '...';
    } else {
      preview = r.error || 'Generation failed';
    }
    
    html += '<div class="article-result-card">';
    html += '  <div class="article-result-header" onclick="toggleArticleResult(this)" data-index="' + i + '">';
    html += '    <div class="result-title">' + icon + ' ' + escapeHtml(preview) + '</div>';
    html += '    <div style="display:flex;align-items:center;gap:8px;">';
    if (success) {
      html += '      <span class="badge badge-success">' + t('done') + '</span>';
    } else {
      html += '      <span class="badge badge-danger">' + t('failed') + '</span>';
    }
    html += '      <i class="fas fa-chevron-right result-chevron"></i>';
    html += '    </div>';
    html += '  </div>';
    html += '  <div class="article-result-body">';
    if (success && r.article) {
      html += '    <div class="markdown-content">' + marked.parse(r.article) + '</div>';
      html += '    <div style="margin-top:12px;display:flex;gap:8px;">';
      html += '      <button class="btn btn-sm btn-secondary" onclick="copyBatchArticle(' + i + ')"><i class="fas fa-copy"></i> ' + t('copy') + '</button>';
      html += '      <button class="btn btn-sm btn-secondary" onclick="downloadBatchArticle(' + i + ')"><i class="fas fa-download"></i> ' + t('downloadMd') + '</button>';
      html += '    </div>';
    } else if (r.error) {
      html += '    <p style="color:var(--danger);">' + escapeHtml(r.error) + '</p>';
    }
    html += '  </div>';
    html += '</div>';
  }
  
  listEl.innerHTML = html;
  
  // Store articles for copy/download
  state._batchArticles = results;
}

function toggleArticleResult(headerEl) {
  headerEl.classList.toggle('open');
  var body = headerEl.nextElementSibling;
  if (body) body.classList.toggle('open');
}

function expandAllResults() {
  document.querySelectorAll('.article-result-card').forEach(function(card) {
    card.querySelector('.article-result-header').classList.add('open');
    card.querySelector('.article-result-body').classList.add('open');
  });
}

function collapseAllResults() {
  document.querySelectorAll('.article-result-card').forEach(function(card) {
    card.querySelector('.article-result-header').classList.remove('open');
    card.querySelector('.article-result-body').classList.remove('open');
  });
}

function copyBatchArticle(index) {
  var articles = state._batchArticles;
  if (!articles || !articles[index]) return;
  var text = articles[index].article;
  if (!text) return;
  navigator.clipboard.writeText(text).then(function() {
    toast('Article copied!', 'success');
  }).catch(function() {
    // Fallback
    var ta = document.createElement('textarea');
    ta.value = text;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    ta.remove();
    toast('Article copied!', 'success');
  });
}

function downloadBatchArticle(index) {
  var articles = state._batchArticles;
  if (!articles || !articles[index]) return;
  var r = articles[index];
  if (!r.article) return;
  var blob = new Blob([r.article], { type: 'text/markdown' });
  var a = document.createElement('a');
  var slug = (r.topic || 'article').replace(/[^a-zA-Z0-9\u0600-\u06FF\s]/g, '').replace(/\s+/g, '-').substring(0, 40).toLowerCase();
  a.download = slug + '.md';
  a.href = URL.createObjectURL(blob);
  a.click();
  URL.revokeObjectURL(a.href);
  toast('Downloaded: ' + a.download, 'success');
}


async function loadProviders() {
  try {
    const data = await api('/api/article/providers');
    const sel = document.getElementById('articleProvider');
    sel.innerHTML = data.providers.map(p => `<option value="${p}" ${p === data.default ? 'selected' : ''}>${p.toUpperCase()}</option>`).join('');
    if (!data.providers.length) sel.innerHTML = '<option value="ollama">Ollama (may be offline)</option>';
  } catch(e) {}
}


/* ==============================================
   Auto-Pipeline Functions
   ============================================== */
function showPipeline() {
  document.getElementById('pipelineOverlay').classList.add('active');
  document.querySelectorAll('.pipeline-step').forEach(function(s) {
    s.className = 'pipeline-step pending';
  });
  document.getElementById('pipelineStatus').textContent = 'Preparing...';
  document.querySelector('.pipeline-step[data-step="1"]').className = 'pipeline-step active';
}

function updatePipelineStep(step, statusText) {
  var stepEl = document.querySelector('.pipeline-step[data-step="' + step + '"]');
  if (stepEl) {
    stepEl.className = 'pipeline-step completed';
  }
  // Activate next step
  var nextStep = step + 1;
  var nextEl = document.querySelector('.pipeline-step[data-step="' + nextStep + '"]');
  if (nextEl) {
    nextEl.className = 'pipeline-step active';
  }
  document.getElementById('pipelineStatus').textContent = statusText || '';
}

function hidePipeline() {
  document.getElementById('pipelineOverlay').classList.remove('active');
}

async function runAutoPipeline(seed, depth, expandModifiers) {
  showPipeline();
  try {
    // Step 1: Running full pipeline (research + cluster + AI)
    updatePipelineStep(1, 'Researching: ' + seed + '...');
    
    var result = await api('/api/pipeline/run', {
      method: 'POST',
      body: JSON.stringify({ seed: seed, depth: depth, expand_modifiers: expandModifiers })
    });
    if (result.error) { hidePipeline(); toast(result.error, 'error'); return null; }
    
    state.keywordData = result.keyword_data;
    state.clusterMap = result.cluster_map;
    state.pipelineResult = result;
    
    updatePipelineStep(1, 'Found ' + result.stats.total_keywords + ' keywords');
    updatePipelineStep(2, result.stats.total_clusters + ' clusters, ' + result.stats.total_articles + ' articles');
    updatePipelineStep(3, 'Analysis complete!');
    
    // Auto-navigate to clusters and render from state
    setTimeout(function() {
      hidePipeline();
      navigate('clusters');
      renderClusterFromState();
      toast('Pipeline complete! ' + result.stats.total_articles + ' articles in plan.', 'success');
    }, 600);

    return result;
  } catch(e) {
    hidePipeline();
    toast('Pipeline failed: ' + e.message, 'error');
    return null;
  }
}

function loadClusterTopics() {
  if (!state.clusterMap || !state.clusterMap.content_plan) {
    toast('No cluster data available. Run the pipeline first.', 'error');
    return;
  }
  var plan = state.clusterMap.content_plan;
  if (!plan.length) { toast('No content plan found.', 'error'); return; }

  // Populate article generator with the first pillar topic
  var first = plan[0];
  document.getElementById('articleTopic').value = first.pillar_title || first.pillar_keyword;

  // Set keywords from all cluster keywords
  var allKws = [];
  plan.forEach(function(pc) {
    allKws.push(pc.pillar_keyword);
    (pc.articles || []).slice(0, 2).forEach(function(a) { allKws.push(a.keyword); });
  });
  document.getElementById('articleKeywords').value = allKws.slice(0, 15).join('\n');

  toast('Loaded ' + plan.length + ' cluster topics. First topic: ' + first.pillar_title, 'success');
}

async function generateArticle() {
  const topic = document.getElementById('articleTopic').value.trim();
  if (!topic) { toast('Enter a topic', 'error'); return; }

  const keywords = document.getElementById('articleKeywords').value.split('\n').map(k => k.trim()).filter(Boolean);
  showLoading('Generating article...');
  document.getElementById('btnGenArticle').disabled = true;
  try {
    const data = await api('/api/article/generate', {
      method: 'POST',
      body: JSON.stringify({
        topic,
        keywords: keywords.length ? keywords : [topic],
        provider: document.getElementById('articleProvider').value,
        word_count: parseInt(document.getElementById('articleWordCount').value),
        tone: document.getElementById('articleTone').value,
        style: document.getElementById('articleStyle').value,
        language: document.getElementById('articleLanguage').value,
      })
    });
    hideLoading();
    if (data.error) { toast(data.error, 'error'); return; }

    state.generatedArticle = data.article;
    state.articleTopic = data.topic;
    document.getElementById('articleResult').style.display = 'block';
    document.getElementById('articleContent').innerHTML = marked.parse(data.article);
    toast('Article generated!', 'success');
  } catch(e) { hideLoading(); toast('Failed: ' + e.message, 'error'); }
  document.getElementById('btnGenArticle').disabled = false;
}

function copyArticle() {
  navigator.clipboard.writeText(state.generatedArticle);
  toast('Copied to clipboard!', 'success');
}

function downloadArticle() {
  const blob = new Blob([state.generatedArticle], { type: 'text/markdown' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = (state.articleTopic || 'article').toLowerCase().replace(/\s+/g, '_') + '.md';
  a.click();
}

/* ══════════════════════════════════════════════
   Export: PDF Audit Report
   ══════════════════════════════════════════════ */
async function exportAuditPdf() {
  if (!state.auditResult) { toast('No audit to export', 'error'); return; }
  showLoading('Generating PDF report...');
  try {
    const res = await fetch(API + '/api/audit/export-pdf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Session-ID': sessionId, ...authHeaders() },
      body: JSON.stringify({ audit_result: state.auditResult })
    });
    hideLoading();
    if (!res.ok) { const e = await res.json(); toast(e.error || 'Export failed', 'error'); return; }
    const blob = await res.blob();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'seo-audit-report.pdf';
    a.click();
    toast('PDF exported!', 'success');
  } catch(e) { hideLoading(); toast('Export failed: ' + e.message, 'error'); }
}

/* ══════════════════════════════════════════════
   Export: CSV Keywords
   ══════════════════════════════════════════════ */
async function exportKeywordsCsv() {
  if (!state.keywordData) { toast('No keyword data to export', 'error'); return; }
  showLoading('Generating CSV...');
  try {
    const res = await fetch(API + '/api/keyword-research/export-csv', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Session-ID': sessionId, ...authHeaders() },
      body: JSON.stringify({ keyword_data: state.keywordData })
    });
    hideLoading();
    if (!res.ok) { const e = await res.json(); toast(e.error || 'Export failed', 'error'); return; }
    const blob = await res.blob();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'keywords-export.csv';
    a.click();
    toast('CSV exported!', 'success');
  } catch(e) { hideLoading(); toast('Export failed: ' + e.message, 'error'); }
}

/* ══════════════════════════════════════════════
   SEO Audit
   ══════════════════════════════════════════════ */
async function runAudit() {
  const url = document.getElementById('auditUrl').value.trim();
  if (!url) { toast('Enter a URL', 'error'); return; }

  showLoading('Auditing URL...');
  document.getElementById('btnAudit').disabled = true;
  try {
    const data = await api('/api/audit', {
      method: 'POST',
      body: JSON.stringify({ url, keyword: document.getElementById('auditKeyword').value.trim(), page_type: document.getElementById('auditPageType').value })
    });
    hideLoading();
    if (data.error && !data.score) { toast(data.error, 'error'); return; }

    state.auditResult = data;
    renderAuditResults(data);
    document.getElementById('btnExportPdf').style.display = 'inline-flex';
    toast('Audit complete!', 'success');
  } catch(e) { hideLoading(); toast('Failed: ' + e.message, 'error'); }
  document.getElementById('btnAudit').disabled = false;
}

function renderAuditResults(data) {
  const container = document.getElementById('auditResults');
  container.style.display = 'block';
  const score = data.score || 0;
  const scoreClass = score >= 80 ? 'excellent' : score >= 50 ? 'good' : 'poor';
  const scoreLabel = score >= 80 ? 'Excellent' : score >= 50 ? 'Good' : 'Needs Work';

  let issuesHtml = '';
  (data.issues || []).forEach(issue => {
    const icon = issue.severity === 'critical' ? '🔴' : issue.severity === 'warning' ? '🟡' : 'ℹ️';
    issuesHtml += `<div class="issue-item ${issue.severity}"><span class="issue-icon">${icon}</span><div><div class="issue-cat">${escapeHtml(issue.category)}</div><div>${escapeHtml(issue.message)}</div></div></div>`;
  });

  const headings = data.headings || {};
  let headingsHtml = '';
  for (let i = 1; i <= 6; i++) {
    const tag = 'h' + i;
    const items = headings[tag] || [];
    if (items.length) {
      headingsHtml += `<div style="margin-bottom:4px;"><strong>${tag.toUpperCase()} (${items.length}):</strong> ${items.map(h => `<span class="badge badge-info" style="margin:2px;">${escapeHtml(h.substring(0,50))}</span>`).join(' ')}</div>`;
    }
  }

  const images = data.images || {};
  const links = data.links || {};
  const ptInfo = data.page_type_info || {};
  const ptInsights = data.page_type_insights || {};
  const pageTypeIcons = { homepage: '🏠', product: '🛒', blog: '📝', generic: '📄' };

  // Page-type insights card
  let insightsHtml = '';
  if (ptInsights.label) {
    const focusHtml = (ptInsights.focus_areas || []).map(f => `<li style="margin:3px 0;">${escapeHtml(f)}</li>`).join('');
    const recsHtml = (ptInsights.recommendations || []).map(r => `<div class="issue-item warning" style="margin-bottom:6px;"><span class="issue-icon">💡</span><div>${escapeHtml(r)}</div></div>`).join('');
    insightsHtml = `
      <div class="card" style="border-left:4px solid var(--accent);">
        <div class="card-header">
          <div class="card-title"><span style="font-size:1.2rem;">${pageTypeIcons[data.page_type] || '📄'}</span> ${escapeHtml(ptInsights.label)}</div>
          <span class="badge badge-purple">${data.page_type}</span>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
          <div>
            <div class="form-label" style="margin-bottom:8px;">Focus Areas</div>
            <ul style="list-style:none;padding:0;font-size:0.88rem;">${focusHtml || '<li style="color:var(--text-muted);">Standard SEO checks</li>'}</ul>
          </div>
          <div>
            <div class="form-label" style="margin-bottom:8px;">Recommendations</div>
            ${recsHtml || '<div style="font-size:0.88rem;color:var(--success);">✅ No page-type-specific issues</div>'}
          </div>
        </div>
      </div>`;
  }

  container.innerHTML = insightsHtml + `
    <div class="metrics-row">
      <div class="metric-card" style="display:flex;flex-direction:column;align-items:center;">
        <div class="score-circle ${scoreClass}"><span class="score-value">${score}</span><span class="score-label">${scoreLabel}</span></div>
      </div>
      <div class="metric-card"><div class="metric-icon purple"><i class="fas fa-font"></i></div><div class="metric-label">Word Count</div><div class="metric-value">${data.word_count || 0}</div></div>
      <div class="metric-card"><div class="metric-icon blue"><i class="fas fa-link"></i></div><div class="metric-label">Internal Links</div><div class="metric-value">${links.internal_count || 0}</div></div>
      <div class="metric-card"><div class="metric-icon green"><i class="fas fa-image"></i></div><div class="metric-label">Images</div><div class="metric-value">${images.total || 0}</div></div>
    </div>

    <div class="card">
      <div class="card-header"><div class="card-title"><i class="fas fa-info-circle"></i> Page Info</div></div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
        <div>
          <div class="form-label">Title</div>
          <div style="font-size:0.9rem;${!data.page_title ? 'color:var(--danger);' : ''}">${data.page_title ? escapeHtml(data.page_title) + ' <span class="badge badge-info">' + data.page_title.length + ' chars</span>' : '<span class="badge badge-danger">MISSING</span>'}</div>
        </div>
        <div>
          <div class="form-label">Meta Description</div>
          <div style="font-size:0.9rem;${!data.meta_description ? 'color:var(--danger);' : ''}">${data.meta_description ? escapeHtml(data.meta_description) + ' <span class="badge badge-info">' + data.meta_description.length + ' chars</span>' : '<span class="badge badge-danger">MISSING</span>'}</div>
        </div>
        <div>
          <div class="form-label">Canonical</div>
          <div style="font-size:0.85rem;word-break:break-all;">${data.canonical ? escapeHtml(data.canonical) : '<span class="badge badge-warning">Missing</span>'}</div>
        </div>
        <div>
          <div class="form-label">Text/HTML Ratio</div>
          <div style="font-size:0.9rem;">${data.text_to_html_ratio || 0}%</div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-header"><div class="card-title"><i class="fas fa-heading"></i> Headings Hierarchy</div></div>
      <div style="font-size:0.88rem;">${headingsHtml || '<div style="color:var(--text-muted);">No headings found.</div>'}</div>
    </div>

    <div class="card">
      <div class="card-header"><div class="card-title"><i class="fas fa-exclamation-triangle"></i> Issues (${(data.issues||[]).length})</div></div>
      <div>${issuesHtml || '<div class="empty-state" style="padding:16px;"><i class="fas fa-check-circle" style="color:var(--success);"></i><p>No issues found — great job!</p></div>'}</div>
    </div>

    <div class="card">
      <div class="card-header"><div class="card-title"><i class="fas fa-image"></i> Images (${images.total || 0})</div></div>
      <div class="metrics-row" style="margin-bottom:0;">
        <div class="metric-card"><div class="metric-label">With Alt Text</div><div class="metric-value" style="color:var(--success);">${images.with_alt || 0}</div></div>
        <div class="metric-card"><div class="metric-label">Without Alt</div><div class="metric-value" style="color:var(--danger);">${images.without_alt || 0}</div></div>
        <div class="metric-card"><div class="metric-label">Alt Coverage</div><div class="metric-value">${images.alt_coverage || 0}%</div></div>
      </div>
    </div>

    <div class="card">
      <div class="card-header"><div class="card-title"><i class="fas fa-link"></i> Links</div></div>
      <div class="metrics-row" style="margin-bottom:0;">
        <div class="metric-card"><div class="metric-label">Internal</div><div class="metric-value">${links.internal_count || 0}</div></div>
        <div class="metric-card"><div class="metric-label">External</div><div class="metric-value">${links.external_count || 0}</div></div>
        <div class="metric-card"><div class="metric-label">Nofollow</div><div class="metric-value">${links.nofollow_count || 0}</div></div>
      </div>
    </div>
  `;
}

/* ══════════════════════════════════════════════
   Batch Audit
   ══════════════════════════════════════════════ */
function handleBatchFile(e) {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (ev) => {
    state.batchCsv = ev.target.result;
    document.getElementById('batchFileInfo').style.display = 'block';
    document.getElementById('batchFileInfo').innerHTML = `<span class="badge badge-info">📎 ${escapeHtml(file.name)} (${(file.size/1024).toFixed(1)} KB)</span>`;
    document.getElementById('btnBatch').disabled = false;
  };
  reader.readAsText(file);
}

async function downloadSampleCsv() {
  const data = await api('/api/batch-audit/sample-csv');
  const blob = new Blob([data.csv], { type: 'text/csv' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'sample.csv';
  a.click();
}

async function runBatchAudit() {
  if (!state.batchCsv) { toast('Upload a CSV first', 'error'); return; }

  showLoading('Running batch audit... (this may take a while)');
  document.getElementById('btnBatch').disabled = true;
  try {
    const data = await api('/api/batch-audit', {
      method: 'POST',
      body: JSON.stringify({ csv: state.batchCsv })
    });
    hideLoading();
    if (data.error) { toast(data.error, 'error'); return; }

    const container = document.getElementById('batchResults');
    container.style.display = 'block';

    const valid = (data.results||[]).filter(r => !r.error || r.page_title);
    const avg = valid.length ? valid.reduce((s,r) => s + (r.score||0), 0) / valid.length : 0;

    container.innerHTML = `
      <div class="metrics-row">
        <div class="metric-card"><div class="metric-icon purple"><i class="fas fa-globe"></i></div><div class="metric-label">URLs Audited</div><div class="metric-value">${data.count || 0}</div></div>
        <div class="metric-card"><div class="metric-icon green"><i class="fas fa-chart-line"></i></div><div class="metric-label">Avg Score</div><div class="metric-value">${avg.toFixed(0)}/100</div></div>
        <div class="metric-card"><div class="metric-icon red"><i class="fas fa-exclamation-circle"></i></div><div class="metric-label">Errors</div><div class="metric-value">${(data.count||0) - valid.length}</div></div>
      </div>
      <div class="card">
        <div class="card-header"><div class="card-title"><i class="fas fa-table"></i> Comparison</div></div>
        <div class="table-wrapper">
          <table>
            <thead><tr><th>URL</th><th>Score</th><th>Title</th><th>Words</th><th>Internal Links</th><th>Images</th><th>Issues</th></tr></thead>
            <tbody>${(data.comparison||[]).map(r => `
              <tr>
                <td style="max-width:250px;font-size:0.85rem;">${escapeHtml(r.URL||'')}</td>
                <td><span class="badge ${(r.Score||0)>=80?'badge-success':(r.Score||0)>=50?'badge-warning':'badge-danger'}">${r.Score||0}</span></td>
                <td style="max-width:200px;font-size:0.85rem;">${escapeHtml((r.Title||'').substring(0,40))}</td>
                <td>${r.Words||0}</td>
                <td>${r['Internal Links']||0}</td>
                <td>${r.Images||0}</td>
                <td>${r.Issues||0}</td>
              </tr>`).join('')}
            </tbody>
          </table>
        </div>
      </div>
    `;
    toast('Batch audit complete!', 'success');
  } catch(e) { hideLoading(); toast('Failed: ' + e.message, 'error'); }
  document.getElementById('btnBatch').disabled = false;
}

/* ══════════════════════════════════════════════
   Recommendations
   ══════════════════════════════════════════════ */
function loadRecommendations() {
  if (state.auditResult) {
    document.getElementById('recNoAudit').style.display = 'none';
    document.getElementById('recContent').style.display = 'block';
    const d = state.auditResult;
    const score = d.score || 0;
    document.getElementById('recAuditInfo').innerHTML = `
      <div class="badge ${score>=80?'badge-success':score>=50?'badge-warning':'badge-danger'}" style="font-size:0.85rem;padding:6px 14px;">
        Auditing: <strong>${escapeHtml(d.final_url || d.url || '')}</strong> — Score: ${score}/100
      </div>`;

    // Quick wins
    const wins = generateQuickWinsLocal(d);
    if (wins.length) {
      document.getElementById('quickWins').innerHTML = wins.map(w => {
        const icon = w.impact === 'High' ? '🔴' : w.impact === 'Medium' ? '🟡' : '🟢';
        return `<div class="issue-item" style="background:var(--bg-input);">
          <span class="issue-icon">${icon}</span>
          <div><div style="font-weight:600;">${escapeHtml(w.action)}</div>
          <div style="font-size:0.8rem;color:var(--text-muted);">Impact: ${w.impact} | Difficulty: ${w.difficulty}</div>
          <div style="font-size:0.8rem;color:var(--accent);margin-top:2px;">💡 ${escapeHtml(w.example)}</div></div>
        </div>`;
      }).join('');
    } else {
      document.getElementById('quickWins').innerHTML = '<div class="empty-state" style="padding:16px;"><i class="fas fa-check-circle" style="color:var(--success);"></i><p>No quick wins — page looks well optimized!</p></div>';
    }
  } else {
    document.getElementById('recNoAudit').style.display = 'block';
    document.getElementById('recContent').style.display = 'none';
  }
}

function generateQuickWinsLocal(data) {
  const wins = [];
  const title = data.page_title || '';
  const desc = data.meta_description || '';
  const wc = data.word_count || 0;
  const imgs = data.images || {};
  const links = data.links || {};
  const ka = data.keyword_analysis || {};

  if (!title) wins.push({ action: 'Add a compelling page title', impact: 'High', difficulty: 'Easy', example: 'Use: Primary Keyword | Secondary - Brand' });
  else if (title.length < 30) wins.push({ action: `Expand title (${title.length} chars, aim 50-60)`, impact: 'High', difficulty: 'Easy', example: 'Add primary keyword and compelling modifier' });

  if (!desc) wins.push({ action: 'Write a meta description with target keyword', impact: 'High', difficulty: 'Easy', example: '150-160 chars, include keyword + CTA' });
  const h1s = (data.headings||{}).h1 || [];
  if (!h1s.length) wins.push({ action: 'Add an H1 tag with primary keyword', impact: 'High', difficulty: 'Easy', example: 'One H1 per page matching search intent' });
  if (wc < 300) wins.push({ action: `Expand content (${wc} words, aim 1500+)`, impact: 'High', difficulty: 'Hard', example: 'Add guides, FAQs, conclusion' });
  if (imgs.without_alt > 0) wins.push({ action: `Add alt text to ${imgs.without_alt} images`, impact: 'Medium', difficulty: 'Easy', example: 'Describe image with relevant keywords' });
  if (!data.canonical) wins.push({ action: 'Add canonical tag', impact: 'Medium', difficulty: 'Easy', example: '<link rel="canonical" href="..." />' });
  if (links.internal_count === 0) wins.push({ action: 'Add internal links to other pages', impact: 'Medium', difficulty: 'Easy', example: 'Link to 3-5 related pages' });

  const impactOrder = { High: 0, Medium: 1, Low: 2 };
  wins.sort((a,b) => (impactOrder[a.impact]||2) - (impactOrder[b.impact]||2));
  return wins;
}

async function generateRecommendations() {
  showLoading('Generating AI recommendations...');
  document.getElementById('btnRecs').disabled = true;
  try {
    const data = await api('/api/recommendations', { method: 'POST', body: '{}' });
    hideLoading();
    if (data.error) { toast(data.error, 'error'); return; }
    document.getElementById('aiRecs').innerHTML = `<div class="markdown-content">${marked.parse(data.recommendations)}</div>`;
    toast('Recommendations generated!', 'success');
  } catch(e) { hideLoading(); toast('Failed: ' + e.message, 'error'); }
  document.getElementById('btnRecs').disabled = false;
}

/* ══════════════════════════════════════════════
   Keyword Tracking
   ══════════════════════════════════════════════ */
async function loadTracking() {
  try {
    const data = await api('/api/tracking');
    const container = document.getElementById('trackedList');
    if (!data.tracked || !data.tracked.length) {
      container.innerHTML = '<div class="empty-state"><i class="fas fa-chart-line"></i><p>No keywords tracked yet. Run keyword research and click "Track Keyword".</p></div>';
      return;
    }
    container.innerHTML = data.tracked.map(item => {
      const latest = item.latest_snapshot || {};
      return `
        <div class="expander">
          <div class="expander-header" onclick="toggleExpander(this)">
            <span>📌 <strong>${escapeHtml(item.keyword)}</strong> — ${item.snapshot_count} snapshot(s)</span>
            <div>
              <button class="btn btn-danger btn-sm" onclick="event.stopPropagation(); deleteTracked('${escapeHtml(item.keyword)}')" style="margin-right:8px;">
                <i class="fas fa-trash"></i>
              </button>
              <i class="fas fa-chevron-right chevron"></i>
            </div>
          </div>
          <div class="expander-body">
            <div class="metrics-row" style="margin-bottom:0;">
              <div class="metric-card"><div class="metric-label">Total Keywords</div><div class="metric-value">${latest.total_keywords||0}</div></div>
              <div class="metric-card"><div class="metric-label">Suggestions</div><div class="metric-value">${latest.suggestions_count||0}</div></div>
              <div class="metric-card"><div class="metric-label">PAA</div><div class="metric-value">${latest.paa_count||0}</div></div>
            </div>
          </div>
        </div>`;
    }).join('');
  } catch(e) { console.error(e); }
}

async function deleteTracked(keyword) {
  await api('/api/tracking/' + encodeURIComponent(keyword), { method: 'DELETE' });
  toast('Keyword removed', 'success');
  loadTracking();
}

/* ══════════════════════════════════════════════
   Content Calendar
   ══════════════════════════════════════════════ */
async function loadCalendar() {
  try {
    const data = await api('/api/calendar');
    if (!data.events || !data.events.length) {
      document.getElementById('calGrid').innerHTML = '';
      document.getElementById('calMetrics').innerHTML = '';
      document.getElementById('calEmpty').style.display = 'block';
      return;
    }
    document.getElementById('calEmpty').style.display = 'none';

    const stats = data.stats || {};
    document.getElementById('calMetrics').innerHTML = `
      <div class="metrics-row">
        <div class="metric-card"><div class="metric-icon purple"><i class="fas fa-calendar"></i></div><div class="metric-label">Total Events</div><div class="metric-value">${stats.total||0}</div></div>
        <div class="metric-card"><div class="metric-icon green"><i class="fas fa-building"></i></div><div class="metric-label">Pillar Pages</div><div class="metric-value">${(stats.by_type||{}).pillar||0}</div></div>
        <div class="metric-card"><div class="metric-icon blue"><i class="fas fa-file-alt"></i></div><div class="metric-label">Cluster Articles</div><div class="metric-value">${(stats.by_type||{}).cluster||0}</div></div>
      </div>`;

    const statusColors = { planned:'#6c757d', in_progress:'#f59e0b', draft:'#3b82f6', review:'#f97316', published:'#10b981', paused:'#ef4444' };
    const statusIcons = { planned:'📋', in_progress:'🔨', draft:'📝', review:'👁️', published:'✅', paused:'⏸️' };

    document.getElementById('calGrid').innerHTML = data.events.map(ev => `
      <div class="calendar-event" style="border-left-color:${statusColors[ev.status]||'#6c757d'}">
        <div class="event-date">${ev.type === 'pillar' ? '🏛️' : '📄'} ${escapeHtml(ev.date)}</div>
        <div class="event-title">${escapeHtml(ev.title)}</div>
        <div class="event-keyword">${escapeHtml(ev.keyword)}</div>
        <div class="event-actions">
          <select class="form-select" style="width:auto;padding:4px 8px;font-size:0.8rem;" onchange="updateEventStatus('${ev.id}', this.value)">
            ${['planned','in_progress','draft','review','published','paused'].map(s => `<option value="${s}" ${s===ev.status?'selected':''}>${statusIcons[s]} ${s.replace('_',' ')}</option>`).join('')}
          </select>
        </div>
      </div>
    `).join('');
  } catch(e) { console.error(e); }
}

async function generateCalendar() {
  showLoading('Generating calendar...');
  try {
    const data = await api('/api/calendar', { method: 'POST', body: '{}' });
    hideLoading();
    if (data.error) { toast(data.error, 'error'); return; }
    toast(`Generated ${data.count} events!`, 'success');
    loadCalendar();
  } catch(e) { hideLoading(); toast('Failed: ' + e.message, 'error'); }
}

async function updateEventStatus(eventId, status) {
  await api('/api/calendar/' + eventId, { method: 'PATCH', body: JSON.stringify({ status }) });
  loadCalendar();
}

async function exportCalendar(fmt) {
  const data = await api('/api/calendar/export/' + fmt);
  if (data.content) {
    const ext = fmt === 'markdown' ? 'md' : 'json';
    const type = fmt === 'markdown' ? 'text/markdown' : 'application/json';
    const blob = new Blob([data.content], { type });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'content_calendar.' + ext;
    a.click();
    toast('Calendar exported!', 'success');
  }
}

/* ══════════════════════════════════════════════
   Audit History
   ══════════════════════════════════════════════ */
async function loadAuditHistory() {
  try {
    const data = await api('/api/audit-history?limit=50');
    if (!data.history || !data.history.length) {
      document.getElementById('historyTable').innerHTML = '';
      document.getElementById('historyEmpty').style.display = 'block';
      return;
    }
    document.getElementById('historyEmpty').style.display = 'none';
    document.getElementById('historyTable').innerHTML = `
      <table>
        <thead><tr><th>Date</th><th>URL</th><th>Score</th><th>Words</th><th>Issues</th></tr></thead>
        <tbody>${data.history.map(h => `
          <tr>
            <td style="white-space:nowrap;">${h.created_at ? new Date(h.created_at).toLocaleDateString() : '—'}</td>
            <td style="max-width:300px;font-size:0.85rem;">${escapeHtml(h.url)}</td>
            <td><span class="badge ${(h.score||0)>=80?'badge-success':(h.score||0)>=50?'badge-warning':'badge-danger'}">${h.score}/100</span></td>
            <td>${h.word_count}</td>
            <td>${h.issues_count}</td>
          </tr>`).join('')}
        </tbody>
      </table>`;
  } catch(e) { console.error(e); }
}

/* ══════════════════════════════════════════════
   Init
   ══════════════════════════════════════════════ */
(async function init() {
  await checkAuth();
  if (authToken) {
    // Restore keyword/cluster data from localStorage
    try {
      var savedKw = localStorage.getItem('rankivo_kw_data');
      if (savedKw) { state.keywordData = JSON.parse(savedKw); }
    } catch(e) {}
    try {
      var savedCluster = localStorage.getItem('rankivo_cluster_data');
      if (savedCluster) { state.clusterMap = JSON.parse(savedCluster); }
    } catch(e) {}
    loadDashboard();
  }
})();


/* ══════════════════════════════════════════════
   Content Gap Analysis
   ══════════════════════════════════════════════ */
let gapData = null;

async function analyzeContentGap() {
  const seed = document.getElementById('gapSeed').value.trim();
  if (!seed) { toast('Enter a target keyword', 'error'); return; }

  const competitorsText = document.getElementById('gapCompetitors').value.trim();
  const myKeywordsText = document.getElementById('gapMyKeywords').value.trim();

  const competitorUrls = competitorsText ? competitorsText.split('\n').map(u => u.trim()).filter(u => u) : [];
  const myKeywords = myKeywordsText ? myKeywordsText.split('\n').map(k => k.trim()).filter(k => k) : [];

  // Show floating progress indicator
  var progressEl = document.createElement('div');
  progressEl.id = 'gapProgress';
  progressEl.style.cssText = 'position:fixed;bottom:24px;right:24px;z-index:9999;padding:12px 20px;background:var(--bg-card);border:1px solid var(--accent);border-radius:var(--radius);box-shadow:0 4px 12px rgba(0,0,0,0.15);font-size:0.88rem;display:flex;align-items:center;gap:10px;min-width:280px;animation:fadeIn 0.3s ease;';
  progressEl.innerHTML = '<span class="spinner" style="width:16px;height:16px;border-width:2px;"></span><span id="gapProgressText">Starting analysis...</span>';
  document.body.appendChild(progressEl);

  var steps = ['Discovering competitors...', 'Fetching page content...', 'Extracting keywords...', 'Comparing keyword sets...', 'Calculating opportunity scores...'];
  var stepIdx = 0;
  var progressInterval = setInterval(function() {
    var el = document.getElementById('gapProgressText');
    if (el && stepIdx < steps.length) {
      el.textContent = steps[stepIdx++];
    } else if (el) {
      el.textContent = 'Almost done...';
    }
  }, 5000);

  document.getElementById('btnGapAnalyze').disabled = true;

  try {
    const data = await api('/api/content-gap/analyze', {
      method: 'POST',
      body: JSON.stringify({
        seed,
        my_keywords: myKeywords,
        competitor_urls: competitorUrls,
        num_serp_results: 5,
        max_competitors: 5,
      })
    });
    clearInterval(progressInterval);
    var progEl = document.getElementById('gapProgress');
    if (progEl) progEl.remove();
    document.getElementById('btnGapAnalyze').disabled = false;

    if (data.error) { toast(data.error, 'error'); return; }

    gapData = data;
    renderGapResults(data);
    toast('Found ' + (data.summary?.total_gaps || 0) + ' content gaps', 'success');
  } catch(e) {
    clearInterval(progressInterval);
    var progEl = document.getElementById('gapProgress');
    if (progEl) progEl.remove();
    document.getElementById('btnGapAnalyze').disabled = false;
    toast('Content gap analysis failed: ' + e.message, 'error');
  }
}

async function discoverCompetitors() {
  const seed = document.getElementById('gapSeed').value.trim();
  if (!seed) { toast('Enter a target keyword first', 'error'); return; }

  showLoading('Discovering competitors from SERP...');
  try {
    const data = await api('/api/content-gap/discover', {
      method: 'POST',
      body: JSON.stringify({ keyword: seed, num_results: 10 })
    });
    hideLoading();

    if (data.error) { toast(data.error, 'error'); return; }

    if (data.competitors && data.competitors.length) {
      const urls = data.competitors.map(c => c.url).filter(u => u).join('\n');
      document.getElementById('gapCompetitors').value = urls;
      toast('Found ' + data.competitors.length + ' competitors', 'success');
    } else {
      toast('No competitors found', 'warning');
    }
  } catch(e) {
    hideLoading();
    toast('Failed to discover competitors', 'error');
  }
}

function renderGapResults(data) {
  document.getElementById('gapResults').style.display = 'block';
  const summary = data.summary || {};
  const gaps = data.gap_analysis?.gap_keywords || [];
  const competitorKws = data.competitor_keywords || [];
  const competitors = data.competitors || [];

  // Stats cards
  document.getElementById('gapStats').innerHTML = `
    <div class="metric-card"><div class="metric-icon red"><i class="fas fa-exclamation-triangle"></i></div><div class="metric-label" data-i18n="contentGapGapsTitle">Content Gaps</div><div class="metric-value">${summary.total_gaps || gaps.length}</div></div>
    <div class="metric-card"><div class="metric-icon blue"><i class="fas fa-key"></i></div><div class="metric-label" data-i18n="contentGapKeywordsTitle">Keywords Found</div><div class="metric-value">${summary.total_competitor_keywords || 0}</div></div>
    <div class="metric-card"><div class="metric-icon green"><i class="fas fa-check-circle"></i></div><div class="metric-label" data-i18n="contentGapCoverageTitle">Coverage</div><div class="metric-value">${data.gap_analysis?.coverage_percentage || 0}%</div></div>
    <div class="metric-card"><div class="metric-icon purple"><i class="fas fa-users"></i></div><div class="metric-label">Competitors</div><div class="metric-value">${summary.competitors_analyzed || 0}</div></div>
  `;

  // Gap keywords list
  if (gaps.length === 0) {
    document.getElementById('gapKeywordsList').innerHTML = '<div class="empty-state" style="padding:24px;"><p data-i18n="contentGapNoResults">No content gaps found!</p></div>';
  } else {
    let html = '';
    gaps.slice(0, 50).forEach((g, i) => {
      const opp = g.opportunity_score || 0;
      const oppColor = opp > 0.5 ? 'var(--danger)' : opp > 0.2 ? 'var(--warning)' : 'var(--success)';
      const oppBg = opp > 0.5 ? 'var(--danger-bg)' : opp > 0.2 ? 'var(--warning-bg)' : 'var(--success-bg)';
      html += '<div style="padding:10px 12px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;">';
      html += '<div><span style="font-weight:600;font-size:0.9rem;">' + escapeHtml(g.keyword) + '</span>';
      html += '<div style="font-size:0.78rem;color:var(--text-muted);">' + g.competitors_using + '/' + g.total_competitors + ' <span data-i18n="contentGapCompetitorsUsing">competitors</span></div></div>';
      html += '<span style="background:' + oppBg + ';color:' + oppColor + ';padding:3px 10px;border-radius:12px;font-size:0.78rem;font-weight:600;">' + (opp * 100).toFixed(0) + '%</span>';
      html += '</div>';
    });
    document.getElementById('gapKeywordsList').innerHTML = html;
  }

  // Competitor keywords
  let cHtml = '';
  competitorKws.slice(0, 50).forEach(kw => {
    cHtml += '<div style="padding:8px 12px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;">';
    cHtml += '<span style="font-size:0.88rem;">' + escapeHtml(kw.keyword) + '</span>';
    cHtml += '<span class="badge badge-info">' + kw.score.toFixed(2) + '</span>';
    cHtml += '</div>';
  });
  document.getElementById('gapCompetitorKwList').innerHTML = cHtml || '<div class="empty-state" style="padding:16px;"><p>No competitor keywords extracted.</p></div>';

  // Competitor details
  let dHtml = '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px;">';
  competitors.forEach(c => {
    dHtml += '<div style="padding:12px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-card);">';
    dHtml += '<div style="font-weight:600;font-size:0.9rem;margin-bottom:4px;">' + escapeHtml(c.title || c.url) + '</div>';
    dHtml += '<div style="font-size:0.8rem;color:var(--accent);margin-bottom:4px;word-break:break-all;">' + escapeHtml(c.url) + '</div>';
    dHtml += '<div style="font-size:0.8rem;color:var(--text-muted);">' + (c.word_count || 0).toLocaleString() + ' words · ' + (c.keywords_found || 0) + ' keywords extracted</div>';
    dHtml += '</div>';
  });
  dHtml += '</div>';
  document.getElementById('gapCompetitorDetails').innerHTML = dHtml;

  // Apply translations
  if (typeof setLanguage === 'function' && currentLanguage) setLanguage(currentLanguage);
}

function exportGapCsv() {
  if (!gapData) { toast('No data to export', 'error'); return; }
  const gaps = gapData.gap_analysis?.gap_keywords || [];
  if (!gaps.length) { toast('No gaps to export', 'error'); return; }

  let csv = 'Keyword,Opportunity Score,Competitors Using,Total Competitors\n';
  gaps.forEach(g => {
    csv += '"' + g.keyword.replace(/"/g, '""') + '",' + g.opportunity_score.toFixed(4) + ',' + g.competitors_using + ',' + g.total_competitors + '\n';
  });

  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'content-gaps-' + (gapData.seed || 'export') + '.csv';
  a.click(); URL.revokeObjectURL(url);
  toast('Exported ' + gaps.length + ' gaps to CSV', 'success');
}


/* ══════════════════════════════════════════════
   Bing Trends
   ══════════════════════════════════════════════ */
let bingTrendsChartInstance = null;

async function loadBingTrendsStatus() {
  try {
    const data = await api('/api/bing/status');
    const el = document.getElementById('bingTrendsStatus');
    el.textContent = data.api_configured ? 'API Connected' : 'API Not Configured';
    el.className = 'badge ' + (data.api_configured ? 'badge-success' : 'badge-warning');
  } catch(e) {
    document.getElementById('bingTrendsStatus').textContent = 'Error';
  }
}

async function loadBingTrends() {
  const kwStr = document.getElementById('bingTrendsKeywords').value.trim();
  if (!kwStr) { toast('Enter at least one keyword', 'error'); return; }
  const keywords = kwStr.split(',').map(k => k.trim()).filter(k => k);
  if (!keywords.length) { toast('Enter valid keywords', 'error'); return; }

  showLoading('Fetching Bing search trends...');
  document.getElementById('btnBingTrends').disabled = true;
  try {
    const data = await api('/api/bing/trends', {
      method: 'POST',
      body: JSON.stringify({
        keywords,
        geo: document.getElementById('bingTrendsGeo').value || '',
      })
    });
    hideLoading();
    document.getElementById('btnBingTrends').disabled = false;
    if (data.error) { toast(data.error, 'error'); return; }

    document.getElementById('bingTrendsResults').style.display = 'block';

    // Chart
    renderBingTrendsChart(data, keywords[0]);

    // Related
    if (data.related && data.related.length) {
      document.getElementById('bingTrendsRelatedContainer').style.display = 'block';
      document.getElementById('bingTrendsRelatedContent').innerHTML = data.related.map(q =>
        '<span class="badge badge-info" style="margin:3px;font-size:0.85rem;">' + escapeHtml(q.query || q) + '</span>'
      ).join('');
    } else {
      document.getElementById('bingTrendsRelatedContainer').style.display = 'none';
    }

    // Trending
    if (data.trending && data.trending.length) {
      document.getElementById('bingTrendsTrending').innerHTML = data.trending.map(function(t) {
        var title = t.title || t.query || t;
        return '<div class="bing-check-row info" style="margin-bottom:4px;"><i class="fas fa-fire" style="color:var(--warning);"></i><span style="font-weight:600;">' + escapeHtml(title) + '</span></div>';
      }).join('');
    } else {
      document.getElementById('bingTrendsTrending').innerHTML = '<div class="empty-state" style="padding:16px;"><p>No trending data available.</p></div>';
    }

    toast('Bing trends loaded!', 'success');
  } catch(e) {
    hideLoading();
    document.getElementById('btnBingTrends').disabled = false;
    toast('Failed: ' + e.message, 'error');
  }
}

function renderBingTrendsChart(data, seed) {
  var ctx = document.getElementById('bingTrendsChart');
  if (bingTrendsChartInstance) bingTrendsChartInstance.destroy();

  var labels = data.dates || [];
  var values = (data.values || {})[seed] || [];

  if (!labels.length || !values.length) {
    bingTrendsChartInstance = new Chart(ctx, {
      type: 'line',
      data: { labels: ['No Data'], datasets: [{ label: seed, data: [0], borderColor: '#6366f1', backgroundColor: 'rgba(99,102,241,0.1)', fill: true }] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: true } } }
    });
    return;
  }

  bingTrendsChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: seed,
        data: values,
        borderColor: '#6366f1',
        backgroundColor: 'rgba(99,102,241,0.12)',
        fill: true,
        tension: 0.4,
        pointRadius: 3,
        pointHoverRadius: 6,
        borderWidth: 2,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { display: true, position: 'top' },
        tooltip: { callbacks: { title: function(items) { return items[0].label; }, label: function(ctx) { return ' Interest: ' + ctx.raw; } } }
      },
      scales: {
        y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' }, ticks: { maxTicksLimit: 6 } },
        x: { grid: { display: false }, ticks: { maxTicksLimit: 10, maxRotation: 45 } }
      },
      interaction: { mode: 'index', intersect: false }
    }
  });
}


/* Intent Training Functions */
async function addIntentWord() {
  var word = document.getElementById('intentWord').value.trim();
  var intent = document.getElementById('intentCategory').value;
  if (!word) { showToast('Enter a word or phrase', 'error'); return; }
  try {
    var res = await (await fetch(API + '/api/intent-training', {
      method: 'POST',
      headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({ word: word, intent: intent })
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    document.getElementById('intentWord').value = '';
    showToast('Added: ' + word + ' -> ' + intent, 'success');
    loadIntentTraining();
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
}

async function loadIntentTraining() {
  try {
    var el = document.getElementById('intentTrainingList');
    if (!el) return;
    var res = await (await fetch(API + '/api/intent-training', { headers: authHeaders() })).json();
    if (res.error) return;
    var data = res.training_data || {};
    var cnt = document.getElementById('intentTrainingCount');
    if (cnt) cnt.textContent = res.total || 0;
    var html = '';
    var colors = { transactional: 'danger', navigational: 'info', informational: 'success', commercial: 'warning' };
    for (var intent in data) {
      var entries = data[intent];
      if (!entries || entries.length === 0) continue;
      html += '<div class="expander">';
      html += '<div class="expander-header" onclick="this.classList.toggle(\"open\");this.nextElementSibling.classList.toggle(\"open\")">';
      html += '<span>' + intent.charAt(0).toUpperCase() + intent.slice(1) + ' (' + entries.length + ')</span>';
      html += '<i class="fas fa-chevron-right chevron"></i></div>';
      html += '<div class="expander-body">';
      for (var i = 0; i < entries.length; i++) {
        var e = entries[i];
        var w = e.word || e;
        var l = e.language || 'auto';
        html += '<div style="display:flex;align-items:center;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--border);">';
        html += '<span style="font-size:0.9rem;"><span class="badge badge-' + (colors[intent]||'info') + '">' + intent + '</span> ' + w + ' <span style="font-size:0.75rem;color:var(--text-muted);">[' + l + ']</span></span>';
        html += '<button class="btn btn-sm btn-danger" onclick="removeIntentWord(this.getAttribute(&quot;data-word&quot;),this.getAttribute(&quot;data-intent&quot;))" data-word="' + w.replace(/"/g, '&quot;') + '" data-intent="' + intent + '"><i class="fas fa-times"></i></button>';
        html += '</div>';
      }
      html += '</div></div>';
    }
    el.innerHTML = html || '<div style="padding:12px;color:var(--text-muted);">No training words yet. Add words above.</div>';
  } catch(e) { console.error('Load intent error:', e); }
}

async function removeIntentWord(word, intent) {
  try {
    await fetch(API + '/api/intent-training', {
      method: 'DELETE',
      headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({ word: word, intent: intent })
    });
    showToast('Removed: ' + word, 'success');
    loadIntentTraining();
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
}

async function testIntentClassifier() {
  var word = document.getElementById('intentWord').value.trim() || 'buy shoes online';
  try {
    var res = await (await fetch(API + '/api/persian-intent/classify', {
      method: 'POST',
      headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({ keyword: word })
    })).json();
    var r = res.result || {};
    var colors = { transactional: 'danger', navigational: 'info', informational: 'success', commercial: 'warning' };
    var html = '<div style="padding:12px;border-radius:8px;background:var(--bg-input);">';
    html += '<strong>&quot;' + word + '&quot;</strong> &rarr; <span class="badge badge-' + (colors[r.intent]||'info') + '">' + (r.intent || 'unknown') + '</span>';
    html += ' (confidence: ' + ((r.confidence||0) * 100).toFixed(0) + '%, method: ' + (r.method||'heuristic') + ')';
    html += '</div>';
    var el = document.getElementById('intentTestResult');
    el.style.display = 'block';
    el.innerHTML = html;
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
}

/* Iran Province Trends */
var provinceChartInstance = null;

async function loadProvinceTrends(keywords) {
  if (!keywords || keywords.length === 0) return;
  var card = document.getElementById('trendsProvinceCard');
  if (!card) return;
  card.style.display = 'block';
  var statusEl = document.getElementById('provinceStatus');
  statusEl.textContent = 'Loading...';
  try {
    var res = await (await fetch(API + '/api/trends/iran-provinces', {
      method: 'POST',
      headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({ keywords: keywords.slice(0, 3) })
    })).json();
    if (res.error) { statusEl.textContent = res.error; return; }
    statusEl.textContent = 'Loaded';
    renderProvinceChart(res.data || {});
    renderProvinceRecommendations(res.data || {});
  } catch(e) { statusEl.textContent = 'Error'; console.error(e); }
}

function renderProvinceChart(data) {
  var canvas = document.getElementById('provinceChart');
  if (!canvas) return;
  if (provinceChartInstance) { provinceChartInstance.destroy(); provinceChartInstance = null; }
  var allP = {};
  var kws = Object.keys(data);
  for (var k = 0; k < kws.length; k++) {
    var provs = data[kws[k]].provinces || [];
    for (var p = 0; p < provs.length; p++) {
      var name = provs[p].name_fa || provs[p].name_en;
      if (!allP[name]) allP[name] = {};
      allP[name][kws[k]] = provs[p].score;
    }
  }
  var sorted = Object.entries(allP).sort(function(a, b) {
    var sA = Object.values(a[1]).reduce(function(s, v) { return s + v; }, 0);
    var sB = Object.values(b[1]).reduce(function(s, v) { return s + v; }, 0);
    return sB - sA;
  }).slice(0, 15);
  var labels = sorted.map(function(x) { return x[0]; });
  var palette = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#3b82f6'];
  var datasets = kws.map(function(kw, i) {
    return {
      label: kw,
      data: sorted.map(function(x) { return (x[1][kw] || 0); }),
      backgroundColor: palette[i % palette.length] + '80',
      borderColor: palette[i % palette.length],
      borderWidth: 1,
      borderRadius: 4
    };
  });
  if (!datasets.length || !labels.length) {
    canvas.parentElement.innerHTML = '<div style="padding:24px;text-align:center;color:var(--text-muted);">No province data available</div>';
    return;
  }
  provinceChartInstance = new Chart(canvas, {
    type: 'bar',
    data: { labels: labels, datasets: datasets },
    options: {
      responsive: true, maintainAspectRatio: false, indexAxis: 'y',
      plugins: { legend: { position: 'top' } },
      scales: { x: { beginAtZero: true, title: { display: true, text: 'Search Interest (0-100)' } } }
    }
  });
}

function renderProvinceRecommendations(data) {
  var html = '';
  for (var kw in data) {
    if (data[kw].recommendation) {
      html += '<div style="padding:10px 14px;border-radius:8px;background:var(--accent-light);margin-bottom:8px;font-size:0.9rem;color:var(--accent);">';
      html += '<i class="fas fa-lightbulb"></i> <strong>' + kw + ':</strong> ' + data[kw].recommendation;
      html += '</div>';
    }
  }
  var el = document.getElementById('provinceRecommendations');
  if (el) el.innerHTML = html;
}

function triggerProvinceTrendsFromKeywords() {
  var kwInput = document.getElementById('trendsKeywords');
  if (kwInput && kwInput.value.trim()) {
    var kws = kwInput.value.split(',').map(function(s) { return s.trim(); }).filter(Boolean);
    if (kws.length > 0) loadProvinceTrends(kws);
  }
}



/* ═══════════════════════════════════════════════
   Phase 2 — Backlink Analysis
   ═══════════════════════════════════════════════ */
async function runBacklinkAnalysis() {
  var domain = document.getElementById('backlinkDomain').value.trim();
  if (!domain) { showToast('Enter a domain', 'error'); return; }
  if (domain.startsWith('http')) { domain = domain.replace(/^https?:\/\//, '').replace(/\/.*$/, ''); }
  var btn = document.getElementById('btnBacklinks');
  btn.disabled = true; btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
  try {
    var res = await (await fetch(API + '/api/backlinks/analyze', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({ domain: domain })
    })).json();
    btn.disabled = false; btn.innerHTML = '<i class="fas fa-search"></i> Analyze';
    if (res.error) { showToast(res.error, 'error'); return; }
    document.getElementById('backlinkResults').style.display = 'block';
    renderBacklinkResults(res);
    showToast('Backlink analysis complete', 'success');
  } catch(e) {
    btn.disabled = false; btn.innerHTML = '<i class="fas fa-search"></i> Analyze';
    showToast('Error: ' + e.message, 'error');
  }
}

function renderBacklinkResults(data) {
  // Stats cards
  var statsHtml = '';
  var stats = [
    { label: 'Total Backlinks', value: data.total_backlinks || 0, icon: 'fa-link', color: '#6366f1' },
    { label: 'Unique Domains', value: data.unique_domains || 0, icon: 'fa-globe', color: '#10b981' },
    { label: 'DoFollow', value: data.dofollow_count || 0, icon: 'fa-check-circle', color: '#3b82f6' },
    { label: 'NoFollow', value: data.nofollow_count || 0, icon: 'fa-times-circle', color: '#f59e0b' },
    { label: 'Toxic', value: data.toxic_count || 0, icon: 'fa-skull-crossbones', color: '#ef4444' },
    { label: 'Avg Domain Auth', value: (data.avg_domain_authority || 0).toFixed(0), icon: 'fa-chart-line', color: '#8b5cf6' }
  ];
  for (var i = 0; i < stats.length; i++) {
    statsHtml += '<div style="padding:16px;border-radius:8px;background:var(--bg-input);text-align:center;">';
    statsHtml += '<div style="font-size:1.5rem;font-weight:700;color:' + stats[i].color + ';">' + stats[i].value + '</div>';
    statsHtml += '<div style="font-size:0.8rem;color:var(--text-muted);margin-top:4px;">' + stats[i].label + '</div>';
    statsHtml += '</div>';
  }
  document.getElementById('backlinkStats').innerHTML = statsHtml;

  // Quality score
  var qs = data.quality_score || 0;
  var qColor = qs >= 70 ? '#10b981' : qs >= 40 ? '#f59e0b' : '#ef4444';
  var qLabel = qs >= 70 ? 'Excellent' : qs >= 50 ? 'Good' : qs >= 30 ? 'Needs Improvement' : 'Poor';
  document.getElementById('linkQualityScore').innerHTML = '<span style="color:' + qColor + ';">' + qs + '</span><span style="font-size:1rem;color:var(--text-muted);">/100</span>';
  document.getElementById('linkQualityLabel').textContent = qLabel;

  // Toxic links
  var toxicHtml = '';
  var toxic = data.toxic_links || [];
  if (toxic.length === 0) {
    toxicHtml = '<div style="padding:12px;color:var(--text-muted);text-align:center;">No toxic links detected</div>';
  } else {
    for (var t = 0; t < Math.min(toxic.length, 20); t++) {
      toxicHtml += '<div style="padding:8px 12px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;">';
      toxicHtml += '<span style="font-size:0.9rem;">' + (toxic[t].domain || toxic[t].url || '') + '</span>';
      toxicHtml += '<span class="badge badge-danger" style="font-size:0.7rem;">' + (toxic[t].reason || 'toxic') + '</span>';
      toxicHtml += '</div>';
    }
  }
  document.getElementById('toxicLinks').innerHTML = toxicHtml;

  // Top linking domains
  var topHtml = '';
  var topDomains = data.top_linking_domains || [];
  if (topDomains.length === 0) {
    topHtml = '<div style="padding:12px;color:var(--text-muted);text-align:center;">No linking domains found</div>';
  } else {
    topHtml = '<table style="width:100%;border-collapse:collapse;font-size:0.9rem;">';
    topHtml += '<tr style="background:var(--bg-input);"><th style="padding:8px 12px;text-align:left;">Domain</th><th style="padding:8px;text-align:right;">Authority</th><th style="padding:8px;text-align:right;">Links</th></tr>';
    for (var d = 0; d < Math.min(topDomains.length, 20); d++) {
      var da = topDomains[d].domain_authority || 0;
      var daColor = da >= 50 ? '#10b981' : da >= 20 ? '#f59e0b' : '#ef4444';
      topHtml += '<tr style="border-bottom:1px solid var(--border);">';
      topHtml += '<td style="padding:8px 12px;">' + (topDomains[d].domain || '') + '</td>';
      topHtml += '<td style="padding:8px;text-align:right;"><span style="color:' + daColor + ';font-weight:600;">' + da + '</span></td>';
      topHtml += '<td style="padding:8px;text-align:right;">' + (topDomains[d].link_count || 0) + '</td>';
      topHtml += '</tr>';
    }
    topHtml += '</table>';
  }
  document.getElementById('topLinkingDomains').innerHTML = topHtml;
}

/* ═══════════════════════════════════════════════
   Phase 2 — SEO Drift Monitoring
   ═══════════════════════════════════════════════ */
async function runDriftAnalysis() {
  var url = document.getElementById('driftUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  if (!url.startsWith('http')) { url = 'https://' + url; }
  var btn = document.getElementById('btnDrift');
  btn.disabled = true; btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Comparing...';
  try {
    var res = await (await fetch(API + '/api/drift/compare', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({ url: url })
    })).json();
    btn.disabled = false; btn.innerHTML = '<i class="fas fa-chart-line"></i> Compare';
    if (res.error) { showToast(res.error, 'error'); return; }
    document.getElementById('driftResults').style.display = 'block';
    renderDriftResults(res);
    showToast('Drift analysis complete', 'success');
  } catch(e) {
    btn.disabled = false; btn.innerHTML = '<i class="fas fa-chart-line"></i> Compare';
    showToast('Error: ' + e.message, 'error');
  }
}

function renderDriftResults(data) {
  // Changes
  var changes = data.changes || [];
  document.getElementById('driftChangeCount').textContent = changes.length;
  var html = '';
  if (changes.length === 0) {
    html = '<div style="padding:20px;text-align:center;color:var(--text-muted);">No snapshots to compare. Run an audit first, then save a snapshot.</div>';
  } else {
    var colorMap = { improved: '#10b981', regressed: '#ef4444', changed: '#f59e0b', unchanged: 'var(--text-muted)' };
    var iconMap = { improved: 'fa-arrow-up', regressed: 'fa-arrow-down', changed: 'fa-exchange-alt', unchanged: 'fa-minus' };
    for (var i = 0; i < changes.length; i++) {
      var c = changes[i];
      var color = colorMap[c.direction] || 'var(--text-muted)';
      var icon = iconMap[c.direction] || 'fa-question';
      html += '<div style="padding:10px 14px;border-left:3px solid ' + color + ';margin-bottom:8px;border-radius:0 8px 8px 0;background:var(--bg-input);">';
      html += '<div style="display:flex;justify-content:space-between;align-items:center;">';
      html += '<span><i class="fas ' + icon + '" style="color:' + color + ';margin-right:8px;"></i><strong>' + (c.metric || '') + '</strong></span>';
      html += '<span style="font-size:0.85rem;color:' + color + ';">' + (c.old_value || 0) + ' → ' + (c.new_value || 0) + ' (' + (c.change_pct || 0) + '%)</span>';
      html += '</div></div>';
    }
  }
  document.getElementById('driftChanges').innerHTML = html;

  // History
  var history = data.history || [];
  var hHtml = '';
  if (history.length === 0) {
    hHtml = '<div style="padding:12px;color:var(--text-muted);text-align:center;">No snapshot history</div>';
  } else {
    hHtml = '<table style="width:100%;border-collapse:collapse;font-size:0.9rem;">';
    hHtml += '<tr style="background:var(--bg-input);"><th style="padding:8px 12px;text-align:left;">Date</th><th style="padding:8px;text-align:right;">Score</th><th style="padding:8px;text-align:right;">Words</th><th style="padding:8px;text-align:right;">Links</th></tr>';
    for (var j = 0; j < history.length; j++) {
      var h = history[j];
      hHtml += '<tr style="border-bottom:1px solid var(--border);">';
      hHtml += '<td style="padding:8px 12px;">' + (h.created_at || h.snapshot_date || '') + '</td>';
      hHtml += '<td style="padding:8px;text-align:right;font-weight:600;">' + (h.score || '-') + '</td>';
      hHtml += '<td style="padding:8px;text-align:right;">' + (h.word_count || '-') + '</td>';
      hHtml += '<td style="padding:8px;text-align:right;">' + (h.total_links || '-') + '</td>';
      hHtml += '</tr>';
    }
    hHtml += '</table>';
  }
  document.getElementById('driftHistory').innerHTML = hHtml;
}

/* ═══════════════════════════════════════════════
   Phase 2 — SPA Rendering
   ═══════════════════════════════════════════════ */
async function checkPlaywrightStatus() {
  try {
    var res = await (await fetch(API + '/api/spa/status', { headers: authHeaders() })).json();
    var el = document.getElementById('playwrightStatus');
    if (!el) return;
    if (res.available) {
      el.className = 'badge badge-success';
      el.textContent = 'Playwright Available';
    } else {
      el.className = 'badge badge-warning';
      el.textContent = 'Playwright Not Installed';
    }
  } catch(e) { console.error(e); }
}

async function runSpaRender() {
  var url = document.getElementById('spaUrl').value.trim();
  var waitTime = parseInt(document.getElementById('spaWaitTime').value) || 3;
  if (!url) { showToast('Enter a URL', 'error'); return; }
  if (!url.startsWith('http')) { url = 'https://' + url; }
  var btn = document.getElementById('btnSpa');
  btn.disabled = true; btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Rendering...';
  try {
    var res = await (await fetch(API + '/api/spa/render', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({ url: url, wait_time: waitTime })
    })).json();
    btn.disabled = false; btn.innerHTML = '<i class="fas fa-play"></i> Render';
    if (res.error) { showToast(res.error, 'error'); return; }
    document.getElementById('spaResults').style.display = 'block';
    renderSpaResults(res);
    showToast('SPA render complete', 'success');
  } catch(e) {
    btn.disabled = false; btn.innerHTML = '<i class="fas fa-play"></i> Render';
    showToast('Error: ' + e.message, 'error');
  }
}

function renderSpaResults(data) {
  // Rendered HTML
  var html = data.rendered_html || '';
  document.getElementById('spaRenderedContent').textContent = html;
  // Word count
  var wc = html.replace(/<[^>]+>/g, '').split(/\s+/).filter(Boolean).length;
  document.getElementById('spaWordCount').textContent = wc + ' words';

  // Stats
  var stats = data.stats || {};
  var statsHtml = '';
  var statItems = [
    { label: 'Render Time', value: (stats.render_time || 0).toFixed(1) + 's' },
    { label: 'Title', value: data.title || 'N/A' },
    { label: 'Final URL', value: data.final_url || data.url || 'N/A' },
    { label: 'Scripts', value: stats.scripts_count || 0 },
    { label: 'Images', value: stats.images_count || 0 },
    { label: 'Meta Tags', value: stats.meta_count || 0 }
  ];
  for (var i = 0; i < statItems.length; i++) {
    statsHtml += '<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--border);font-size:0.9rem;">';
    statsHtml += '<span style="color:var(--text-muted);">' + statItems[i].label + '</span>';
    statsHtml += '<span style="font-weight:600;">' + statItems[i].value + '</span>';
    statsHtml += '</div>';
  }
  document.getElementById('spaRenderStats').innerHTML = statsHtml;

  // Extracted content
  var content = data.content || {};
  var cHtml = '';
  if (content.headings) {
    cHtml += '<div style="margin-bottom:12px;"><strong style="font-size:0.85rem;color:var(--text-muted);">HEADINGS</strong><ul style="list-style:none;padding:0;margin:0;">';
    for (var tag in content.headings) {
      var headings = content.headings[tag];
      for (var h = 0; h < headings.length; h++) {
        cHtml += '<li style="padding:4px 0;font-size:0.85rem;"><code style="color:var(--accent);">' + tag + '</code> ' + headings[h] + '</li>';
      }
    }
    cHtml += '</ul></div>';
  }
  if (content.meta) {
    cHtml += '<div><strong style="font-size:0.85rem;color:var(--text-muted);">META</strong><ul style="list-style:none;padding:0;margin:0;">';
    for (var mk in content.meta) {
      cHtml += '<li style="padding:4px 0;font-size:0.85rem;"><code>' + mk + '</code>: ' + (content.meta[mk] || '') + '</li>';
    }
    cHtml += '</ul></div>';
  }
  document.getElementById('spaExtractedContent').innerHTML = cHtml || '<div style="padding:12px;color:var(--text-muted);">No content extracted</div>';
}


/* ══════════════════════════════════════════════
   Enhanced Orchestrator Functions
   ══════════════════════════════════════════════ */

function getSelectedModules() {
  var modules = [];
  document.querySelectorAll('#orchModuleSelector input[type="checkbox"]:checked').forEach(function(cb) {
    modules.push(cb.getAttribute('data-module'));
  });
  return modules;
}

function updateModuleCount() {
  var count = getSelectedModules().length;
  document.getElementById('orchModuleCount').textContent = count + ' module' + (count !== 1 ? 's' : '') + ' selected';
}

function selectAllModules(select) {
  document.querySelectorAll('#orchModuleSelector input[type="checkbox"]').forEach(function(cb) {
    cb.checked = select;
  });
  updateModuleCount();
}

async function runFullOrchestrator() {
  var url = document.getElementById('orchUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  var workers = parseInt(document.getElementById('orchWorkers').value) || 6;
  var modules = getSelectedModules();
  if (modules.length === 0) { showToast('Select at least one module', 'error'); return; }

  document.getElementById('orchProgress').style.display = 'block';
  document.getElementById('orchResults').style.display = 'none';
  btnLoading('btnOrch', true);

  // Show module progress
  var progressHtml = '';
  modules.forEach(function(m) {
    progressHtml += '<div class="pipeline-step pending" id="orchMod_' + m + '"><span class="pipeline-status"><i class="fas fa-circle" style="font-size:0.5rem;"></i></span> ' + m.replace(/_/g, ' ') + '</div>';
  });
  document.getElementById('orchModuleProgress').innerHTML = progressHtml;
  document.getElementById('orchProgressPct').textContent = '0%';

  try {
    // Use focused endpoint with selected modules
    var res = await (await fetch(API + '/api/orchestrator/focused', {
      method: 'POST',
      headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url, modules: modules, max_workers: workers})
    })).json();

    document.getElementById('orchProgress').style.display = 'none';
    var el = document.getElementById('orchResults');
    el.style.display = 'block';

    var score = res.overall_score || 0;
    var grade = res.grade || 'N/A';
    var scoreColor = score >= 80 ? 'success' : score >= 50 ? 'warning' : 'danger';
    var html = '<div class="card"><div class="card-header"><div class="card-title"><i class="fas fa-layer-group"></i> Full Audit Results <span class="badge badge-' + scoreColor + '">' + score + '/100 (' + grade + ')</span></div></div>';
    html += '<div class="metrics-row">';
    html += '<div class="metric-card"><div class="metric-icon ' + scoreColor + '"><i class="fas fa-star"></i></div><div class="metric-label">Score</div><div class="metric-value">' + score + '</div></div>';
    html += '<div class="metric-card"><div class="metric-icon purple"><i class="fas fa-cogs"></i></div><div class="metric-label">Modules Run</div><div class="metric-value">' + (res.modules_run||0) + '</div></div>';
    html += '<div class="metric-card"><div class="metric-icon red"><i class="fas fa-exclamation-circle"></i></div><div class="metric-label">Critical</div><div class="metric-value">' + ((res.issues_summary||{}).critical||0) + '</div></div>';
    html += '<div class="metric-card"><div class="metric-icon yellow"><i class="fas fa-exclamation-triangle"></i></div><div class="metric-label">Warnings</div><div class="metric-value">' + ((res.issues_summary||{}).warnings||0) + '</div></div>';
    html += '</div>';

    // Module scores breakdown
    var modScores = res.module_scores || {};
    if (Object.keys(modScores).length > 0) {
      html += '<div style="margin-top:12px;padding:12px;background:var(--bg-input);border-radius:8px;"><strong style="font-size:0.85rem;">Module Scores:</strong><div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px;margin-top:8px;">';
      for (var mod in modScores) {
        var ms = modScores[mod];
        var mc = ms >= 80 ? 'success' : ms >= 50 ? 'warning' : 'danger';
        html += '<div style="display:flex;justify-content:space-between;padding:6px 10px;border-radius:6px;background:var(--bg-card);font-size:0.85rem;"><span>' + mod.replace(/_/g, ' ') + '</span><span class="badge badge-' + mc + '">' + ms + '/100</span></div>';
      }
      html += '</div></div>';
    }

    var recs = res.recommendations || [];
    if (recs.length > 0) {
      html += '<div style="margin-top:12px;padding:12px;background:var(--success-bg);border-radius:8px;"><strong>Top Recommendations:</strong>';
      recs.slice(0,10).forEach(function(r) { var t = typeof r === 'string' ? r : (r.action || r.message || JSON.stringify(r)); html += '<div style="padding:4px 0;font-size:0.88rem;">• ' + t + '</div>'; });
      html += '</div>';
    }
    html += '</div>';
    el.innerHTML = html;
    showToast('Audit complete! Score: ' + score + '/100', 'success');
  } catch(e) {
    document.getElementById('orchProgress').style.display = 'none';
    showToast('Error: ' + e.message, 'error');
  }
  btnLoading('btnOrch', false);
}

/* ══════════════════════════════════════════════
   Site Performance Monitoring Functions
   ══════════════════════════════════════════════ */

var perfScoreChartInst = null, perfCWVChartInst = null;

async function loadPerformanceDashboard() {
  var url = document.getElementById('perfUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  var days = parseInt(document.getElementById('perfPeriod').value) || 30;
  btnLoading('btnPerfDash', true);
  try {
    var res = await (await fetch(API + '/api/performance/dashboard', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url, days: days})
    })).json();

    document.getElementById('perfScoreCards').style.display = 'block';
    document.getElementById('perfEmpty').style.display = 'none';

    var cur = res.current || {};
    document.getElementById('perfOverall').textContent = (cur.overall_score || 0) + '/100';
    document.getElementById('perfGrade').textContent = res.grade || 'N/A';
    document.getElementById('perfCWV').textContent = (res.cwv_status || 'unknown').replace('_', ' ');
    document.getElementById('perfIssues').textContent = cur.issues_count || 0;
    document.getElementById('perfSeoScore').textContent = (cur.seo_score || 0);
    document.getElementById('perfTechScore').textContent = (cur.technical_score || 0);
    document.getElementById('perfContentScore').textContent = (cur.content_score || 0);

    // Score trend chart
    var trend = res.score_trend || [];
    if (trend.length > 0) {
      renderPerfScoreChart(trend);
    }
    // CWV trend chart
    var cwvTrend = res.cwv_trend || [];
    if (cwvTrend.length > 0) {
      renderPerfCWVChart(cwvTrend);
    }
    // Tracked sites
    loadTrackedSites();
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnPerfDash', false);
}

function renderPerfScoreChart(data) {
  var canvas = document.getElementById('perfScoreChart');
  if (!canvas) return;
  if (perfScoreChartInst) perfScoreChartInst.destroy();
  perfScoreChartInst = new Chart(canvas, {
    type: 'line',
    data: {
      labels: data.map(function(d) { return d.date; }),
      datasets: [{
        label: 'Overall Score',
        data: data.map(function(d) { return d.score; }),
        borderColor: '#6366f1', backgroundColor: '#6366f120',
        fill: true, tension: 0.4, pointRadius: 4
      }]
    },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { min: 0, max: 100 } } }
  });
}

function renderPerfCWVChart(data) {
  var canvas = document.getElementById('perfCWVChart');
  if (!canvas) return;
  if (perfCWVChartInst) perfCWVChartInst.destroy();
  perfCWVChartInst = new Chart(canvas, {
    type: 'line',
    data: {
      labels: data.map(function(d) { return d.date; }),
      datasets: [
        { label: 'Performance', data: data.map(function(d) { return d.perf; }), borderColor: '#6366f1', tension: 0.4, yAxisID: 'y' },
        { label: 'LCP (ms)', data: data.map(function(d) { return d.lcp; }), borderColor: '#ef4444', tension: 0.4, yAxisID: 'y1' }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: {
        y: { position: 'left', min: 0, max: 100, title: { display: true, text: 'Perf Score' } },
        y1: { position: 'right', min: 0, title: { display: true, text: 'LCP (ms)' }, grid: { drawOnChartArea: false } }
      }
    }
  });
}

async function fetchCWV() {
  var url = document.getElementById('perfUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  showToast('Fetching Core Web Vitals... (may take 30s)', 'info');
  try {
    var res = await (await fetch(API + '/api/performance/fetch-cwv', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    showToast('CWV fetched! Performance score: ' + (res.performance_score || 0), 'success');
    loadPerformanceDashboard();
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
}

async function savePerfSnapshot() {
  var url = document.getElementById('perfUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  try {
    var res = await (await fetch(API + '/api/performance/save-snapshot', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url, audit_data: {score: 75, word_count: 1500, issues: [], headings: {h2: ['a','b','c']}, links: {internal_count: 5, external_count: 2}, images: {total: 3}}})
    })).json();
    showToast('Snapshot saved!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
}

async function generateCombinedReport() {
  var url = document.getElementById('perfUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  showToast('Running full parallel audit + generating report...', 'info');
  btnLoading('btnPerfDash', true);
  try {
    var res = await (await fetch(API + '/api/report/full-audit', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url, max_workers: 6})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    var reportPath = (res.report || {}).report_path || '';
    showToast('Full report generated! Score: ' + ((res.audit || {}).overall_score || 0), 'success');
    if (reportPath) {
      showToast('Report saved to: ' + reportPath, 'info');
    }
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnPerfDash', false);
}

async function loadTrackedSites() {
  try {
    var res = await (await fetch(API + '/api/performance/tracked-sites', { headers: authHeaders() })).json();
    var sites = res.sites || [];
    var el = document.getElementById('perfTrackedSites');
    if (sites.length === 0) { el.innerHTML = '<div style="padding:12px;color:var(--text-muted);">No tracked sites yet.</div>'; return; }
    var html = '<div class="table-wrapper"><table><tr><th>URL</th><th>Score</th><th>Issues</th><th>Last Audit</th></tr>';
    sites.forEach(function(s) {
      var sc = s.score || 0;
      var mc = sc >= 80 ? 'success' : sc >= 50 ? 'warning' : 'danger';
      html += '<tr><td style="max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">' + (s.url||'') + '</td>';
      html += '<td><span class="badge badge-' + mc + '">' + sc + '/100</span></td>';
      html += '<td>' + (s.issues||0) + '</td>';
      html += '<td style="font-size:0.8rem;color:var(--text-muted);">' + (s.last_audit||'').substring(0,10) + '</td></tr>';
    });
    html += '</table></div>';
    el.innerHTML = html;
  } catch(e) { console.error(e); }
}


/* ══════════════════════════════════════════════
   New Module JS Functions
   ══════════════════════════════════════════════ */

function renderGenericResult(data, containerId, title) {
  var el = document.getElementById(containerId);
  if (!el) return;
  el.style.display = 'block';
  var score = data.score || data.composite_score || 0;
  var scoreColor = score >= 80 ? 'success' : score >= 50 ? 'warning' : 'danger';
  var html = '<div class="card"><div class="card-header"><div class="card-title">' + title;
  html += ' <span class="badge badge-' + scoreColor + '">' + score + '/100</span></div></div>';

  var issues = data.issues || [];
  if (issues.length > 0) {
    issues.forEach(function(i) {
      var sev = i.severity || 'info';
      var icon = sev === 'critical' ? 'fa-times-circle' : sev === 'warning' ? 'fa-exclamation-triangle' : 'fa-info-circle';
      html += '<div class="issue-item ' + sev + '"><i class="fas ' + icon + ' issue-icon"></i><div><div class="issue-cat">' + (i.severity||'') + '</div>' + (i.message || JSON.stringify(i)) + '</div></div>';
    });
  }
  var recs = data.recommendations || [];
  if (recs.length > 0) {
    html += '<div style="margin-top:12px;padding:12px;background:var(--success-bg);border-radius:8px;">';
    html += '<strong style="font-size:0.85rem;">💡 Recommendations:</strong>';
    recs.forEach(function(r) {
      var text = typeof r === 'string' ? r : (r.action || r.message || JSON.stringify(r));
      html += '<div style="padding:4px 0;font-size:0.88rem;color:var(--text-secondary);">• ' + text + '</div>';
    });
    html += '</div>';
  }
  html += '</div>';
  el.innerHTML = html;
}

async function runImageAnalysis() {
  var url = document.getElementById('imageUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnImages', true);
  try {
    var res = await (await fetch(API + '/api/images/analyze', { method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}), body: JSON.stringify({url: url}) })).json();
    renderGenericResult(res, 'imageResults', '<i class="fas fa-images"></i> Image Optimization');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnImages', false);
}

async function runSitemapAudit() {
  var url = document.getElementById('sitemapUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnSitemapAudit', true);
  try {
    var res = await (await fetch(API + '/api/sitemap/audit', { method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}), body: JSON.stringify({url: url}) })).json();
    renderGenericResult(res, 'sitemapResults', '<i class="fas fa-sitemap"></i> Sitemap Audit');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnSitemapAudit', false);
}

async function runHreflangAudit() {
  var url = document.getElementById('hreflangUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnHreflang', true);
  try {
    var res = await (await fetch(API + '/api/hreflang/audit', { method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}), body: JSON.stringify({url: url}) })).json();
    renderGenericResult(res, 'hreflangResults', '<i class="fas fa-globe"></i> Hreflang Audit');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnHreflang', false);
}

async function runLocalSeoAudit() {
  var url = document.getElementById('localUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnLocalSeo', true);
  try {
    var res = await (await fetch(API + '/api/local-seo/audit', { method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}), body: JSON.stringify({url: url}) })).json();
    renderGenericResult(res, 'localResults', '<i class="fas fa-map-marker-alt"></i> Local SEO');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnLocalSeo', false);
}

async function runEcommerceAudit() {
  var url = document.getElementById('ecomUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnEcom', true);
  try {
    var res = await (await fetch(API + '/api/ecommerce/audit', { method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}), body: JSON.stringify({url: url}) })).json();
    renderGenericResult(res, 'ecomResults', '<i class="fas fa-shopping-cart"></i> E-commerce SEO');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnEcom', false);
}

async function runSxoAudit() {
  var url = document.getElementById('sxoUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnSxo', true);
  try {
    var res = await (await fetch(API + '/api/sxo/audit', { method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}), body: JSON.stringify({url: url}) })).json();
    renderGenericResult(res, 'sxoResults', '<i class="fas fa-user-check"></i> SXO Audit');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnSxo', false);
}

async function runContentBrief() {
  var topic = document.getElementById('briefTopic').value.trim();
  if (!topic) { showToast('Enter a topic', 'error'); return; }
  var kw = document.getElementById('briefKeywords').value.split(',').map(function(s){return s.trim()}).filter(Boolean);
  if (kw.length === 0) kw = [topic];
  btnLoading('btnBrief', true);
  try {
    var res = await (await fetch(API + '/api/content-brief/generate', { method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}), body: JSON.stringify({topic: topic, keywords: kw, intent: document.getElementById('briefIntent').value, language: document.getElementById('briefLang').value}) })).json();
    renderGenericResult(res, 'briefResults', '<i class="fas fa-file-alt"></i> Content Brief');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnBrief', false);
}

async function runProgSeoAudit() {
  var url = document.getElementById('progUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnProg', true);
  try {
    var res = await (await fetch(API + '/api/programmatic/audit', { method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}), body: JSON.stringify({url: url}) })).json();
    renderGenericResult(res, 'progResults', '<i class="fas fa-cubes"></i> Programmatic SEO');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnProg', false);
}

async function runSeoPlan() {
  var industry = document.getElementById('planIndustry').value;
  try {
    var res = await (await fetch(API + '/api/plan/generate', { method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}), body: JSON.stringify({industry: industry}) })).json();
    var el = document.getElementById('planResults');
    el.style.display = 'block';
    var html = '<div class="card"><div class="card-header"><div class="card-title">' + (res.icon||'') + ' ' + (res.label||industry) + ' SEO Strategy</div></div>';
    html += '<div class="metrics-row">';
    (res.focus_areas||[]).slice(0,4).forEach(function(f) { html += '<div class="metric-card"><div class="metric-icon purple"><i class="fas fa-bullseye"></i></div><div class="metric-label">Focus</div><div class="metric-value" style="font-size:1rem;">' + f + '</div></div>'; });
    html += '</div>';
    (res.implementation_phases||[]).forEach(function(p) {
      html += '<div class="expander"><div class="expander-header" onclick="this.classList.toggle(\'open\');this.nextElementSibling.classList.toggle(\'open\')">';
      html += '<span>Phase ' + p.phase + ' (' + p.timeline + ')</span><i class="fas fa-chevron-right chevron"></i></div>';
      html += '<div class="expander-body"><ul style="list-style:disc;padding-left:20px;">';
      (p.tasks||[]).forEach(function(t) { html += '<li style="padding:3px 0;">' + t + '</li>'; });
      html += '</ul></div></div>';
    });
    html += '</div>';
    el.innerHTML = html;
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
}

async function runFullOrchestrator() {
  var url = document.getElementById('orchUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  var workers = parseInt(document.getElementById('orchWorkers').value) || 6;
  document.getElementById('orchProgress').style.display = 'block';
  btnLoading('btnOrch', true);
  try {
    var res = await (await fetch(API + '/api/orchestrator/audit', { method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}), body: JSON.stringify({url: url, max_workers: workers}) })).json();
    document.getElementById('orchProgress').style.display = 'none';
    var el = document.getElementById('orchResults');
    el.style.display = 'block';
    var score = res.overall_score || 0;
    var grade = res.grade || 'N/A';
    var scoreColor = score >= 80 ? 'success' : score >= 50 ? 'warning' : 'danger';
    var html = '<div class="card"><div class="card-header"><div class="card-title"><i class="fas fa-layer-group"></i> Full Audit Results <span class="badge badge-' + scoreColor + '">' + score + '/100 (' + grade + ')</span></div></div>';
    html += '<div class="metrics-row">';
    html += '<div class="metric-card"><div class="metric-icon ' + scoreColor + '"><i class="fas fa-star"></i></div><div class="metric-label">Score</div><div class="metric-value">' + score + '</div></div>';
    html += '<div class="metric-card"><div class="metric-icon purple"><i class="fas fa-cogs"></i></div><div class="metric-label">Modules Run</div><div class="metric-value">' + (res.modules_run||0) + '</div></div>';
    html += '<div class="metric-card"><div class="metric-icon red"><i class="fas fa-exclamation-circle"></i></div><div class="metric-label">Critical</div><div class="metric-value">' + ((res.issues_summary||{}).critical||0) + '</div></div>';
    html += '<div class="metric-card"><div class="metric-icon yellow"><i class="fas fa-exclamation-triangle"></i></div><div class="metric-label">Warnings</div><div class="metric-value">' + ((res.issues_summary||{}).warnings||0) + '</div></div>';
    html += '</div>';
    var recs = res.recommendations || [];
    if (recs.length > 0) {
      html += '<div style="margin-top:12px;padding:12px;background:var(--success-bg);border-radius:8px;"><strong>Top Recommendations:</strong>';
      recs.slice(0,10).forEach(function(r) { var t = typeof r === 'string' ? r : (r.action || r.message || JSON.stringify(r)); html += '<div style="padding:4px 0;font-size:0.88rem;">• ' + t + '</div>'; });
      html += '</div>';
    }
    html += '</div>';
    el.innerHTML = html;
  } catch(e) {
    document.getElementById('orchProgress').style.display = 'none';
    showToast('Error: ' + e.message, 'error');
  }
  btnLoading('btnOrch', false);
}

function btnLoading(id, loading) {
  var btn = document.getElementById(id);
  if (!btn) return;
  if (loading) { btn.disabled = true; btn.dataset.origHtml = btn.innerHTML; btn.innerHTML = '<span class="spinner"></span> Running...'; }
  else { btn.disabled = false; if (btn.dataset.origHtml) btn.innerHTML = btn.dataset.origHtml; }
}


/* ══════════════════════════════════════════════
   Button Handler Functions (injected)
   ══════════════════════════════════════════════ */

async function runEeatAnalysis() {
  var url = document.getElementById('eeatUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnEeat', true);
  try {
    var res = await (await fetch(API + '/api/eeat/analyze', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    renderGenericResult('eeatResults', res, 'E-E-A-T Analysis');
    showToast('E-E-A-T analysis complete!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnEeat', false);
}

async function runSchemaDeepAudit() {
  var url = document.getElementById('schemaDeepUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnSchemaDeep', true);
  try {
    var res = await (await fetch(API + '/api/schema/audit', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    renderGenericResult('schemaDeepResults', res, 'Schema Audit');
    showToast('Schema audit complete!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnSchemaDeep', false);
}

async function runGeoAudit() {
  var url = document.getElementById('geoUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnGeo', true);
  try {
    var res = await (await fetch(API + '/api/geo/audit', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    renderGenericResult('geoResults', res, 'GEO / AI Search Audit');
    showToast('GEO audit complete!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnGeo', false);
}

async function runImageAnalysis() {
  var url = document.getElementById('imageUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnImages', true);
  try {
    var res = await (await fetch(API + '/api/images/analyze', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    renderGenericResult('imageResults', res, 'Image SEO Analysis');
    showToast('Image analysis complete!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnImages', false);
}

async function runSitemapAudit() {
  var url = document.getElementById('sitemapUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnSitemap', true);
  try {
    var res = await (await fetch(API + '/api/sitemap/audit', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    renderGenericResult('sitemapResults', res, 'Sitemap Audit');
    showToast('Sitemap audit complete!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnSitemap', false);
}

async function runHreflangAudit() {
  var url = document.getElementById('hreflangUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnHreflang', true);
  try {
    var res = await (await fetch(API + '/api/hreflang/audit', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    renderGenericResult('hreflangResults', res, 'Hreflang Audit');
    showToast('Hreflang audit complete!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnHreflang', false);
}

async function runLocalSeoAudit() {
  var url = document.getElementById('localSeoUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnLocalSeo', true);
  try {
    var res = await (await fetch(API + '/api/local-seo/audit', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    renderGenericResult('localSeoResults', res, 'Local SEO Audit');
    showToast('Local SEO audit complete!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnLocalSeo', false);
}

async function runEcommerceAudit() {
  var url = document.getElementById('ecommerceUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnEcommerce', true);
  try {
    var res = await (await fetch(API + '/api/ecommerce/audit', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    renderGenericResult('ecommerceResults', res, 'E-commerce SEO Audit');
    showToast('E-commerce audit complete!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnEcommerce', false);
}

async function runSxoAudit() {
  var url = document.getElementById('sxoUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnSxo', true);
  try {
    var res = await (await fetch(API + '/api/sxo/audit', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    renderGenericResult('sxoResults', res, 'SXO Audit');
    showToast('SXO audit complete!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnSxo', false);
}

async function runContentBrief() {
  var topic = document.getElementById('briefTopic').value.trim();
  if (!topic) { showToast('Enter a topic', 'error'); return; }
  btnLoading('btnBrief', true);
  try {
    var res = await (await fetch(API + '/api/content-brief/generate', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({topic: topic, keywords: [topic]})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    renderGenericResult('briefResults', res, 'Content Brief');
    showToast('Content brief generated!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnBrief', false);
}

async function runProgSeoAudit() {
  var url = document.getElementById('progSeoUrl').value.trim();
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnProgSeo', true);
  try {
    var res = await (await fetch(API + '/api/programmatic/audit', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    renderGenericResult('progSeoResults', res, 'Programmatic SEO Audit');
    showToast('Programmatic SEO audit complete!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnProgSeo', false);
}

async function runSeoPlan() {
  var industry = document.getElementById('seoPlanIndustry') ? document.getElementById('seoPlanIndustry').value : 'saas';
  btnLoading('btnSeoPlan', true);
  try {
    var res = await (await fetch(API + '/api/plan/generate', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({industry: industry})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    renderGenericResult('seoPlanResults', res, 'SEO Strategy Plan');
    showToast('SEO plan generated!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnSeoPlan', false);
}

async function loadTrends() {
  var kw = document.getElementById('trendsKeyword') ? document.getElementById('trendsKeyword').value.trim() : '';
  if (!kw) { showToast('Enter a keyword', 'error'); return; }
  try {
    var res = await (await fetch(API + '/api/trends/interest-over-time', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({keywords: [kw]})
    })).json();
    showToast('Trends loaded for: ' + kw, 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
}

async function runBingAnalysis() {
  var url = document.getElementById('bingUrl') ? document.getElementById('bingUrl').value.trim() : '';
  if (!url) { showToast('Enter a URL', 'error'); return; }
  btnLoading('btnBing', true);
  try {
    var res = await (await fetch(API + '/api/bing/analyze', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url})
    })).json();
    showToast('Bing analysis complete!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
  btnLoading('btnBing', false);
}

async function checkBingIndex() {
  var url = document.getElementById('bingUrl') ? document.getElementById('bingUrl').value.trim() : '';
  if (!url) { showToast('Enter a URL', 'error'); return; }
  try {
    var res = await (await fetch(API + '/api/bing/index-status', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url})
    })).json();
    showToast('Index check complete!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
}

async function submitToBing() {
  var url = document.getElementById('bingUrl') ? document.getElementById('bingUrl').value.trim() : '';
  if (!url) { showToast('Enter a URL', 'error'); return; }
  try {
    var res = await (await fetch(API + '/api/bing/submit', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({url: url})
    })).json();
    showToast('URL submitted to Bing!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
}

async function changeMyPassword() {
  var oldPw = document.getElementById('oldPassword') ? document.getElementById('oldPassword').value : '';
  var newPw = document.getElementById('newPassword') ? document.getElementById('newPassword').value : '';
  if (!oldPw || !newPw) { showToast('Enter both passwords', 'error'); return; }
  try {
    var res = await (await fetch(API + '/api/auth/change-password', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({old_password: oldPw, new_password: newPw})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    showToast('Password changed!', 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
}

async function createNewUser() {
  var u = document.getElementById('newUsername') ? document.getElementById('newUsername').value.trim() : '';
  var p = document.getElementById('newUserPassword') ? document.getElementById('newUserPassword').value : '';
  var r = document.getElementById('newUserRole') ? document.getElementById('newUserRole').value : 'user';
  if (!u || !p) { showToast('Enter username and password', 'error'); return; }
  try {
    var res = await (await fetch(API + '/api/users', {
      method: 'POST', headers: Object.assign({}, authHeaders(), {'Content-Type': 'application/json'}),
      body: JSON.stringify({username: u, password: p, role: r})
    })).json();
    if (res.error) { showToast(res.error, 'error'); return; }
    showToast('User created: ' + u, 'success');
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
}



/* Settings Page Functions */
async function loadUsers() {
  try {
    var res = await fetch(API + '/api/users', { headers: authHeaders() });
    var data = await res.json();
    var el = document.getElementById('usersList');
    if (!el) return;
    var users = data.users || [];
    if (users.length === 0) { el.innerHTML = '<div style="padding:12px;color:var(--text-muted);">No users found.</div>'; return; }
    var html = '<div class="table-wrapper"><table><tr><th>Username</th><th>Role</th><th>Email</th><th>Last Login</th><th></th></tr>';
    users.forEach(function(u) {
      html += '<tr><td>' + u.username + '</td><td><span class="badge badge-"' + (u.role==='admin'?'purple':'info') + '>' + u.role + '</span></td>';
      html += '<td>' + (u.email||'-') + '</td>';
      html += '<td style="font-size:0.8rem;color:var(--text-muted);">' + (u.last_login||'never').substring(0,16) + '</td>';
      html += '<td><button class="btn btn-sm btn-danger" onclick="deleteUser(&quot;"+u.username+"&quot;)"><i class="fas fa-times"></i></button></td></tr>';
    });
    html += '</table></div>';
    el.innerHTML = html;
  } catch(e) { console.error('loadUsers error:', e); }
}

async function loadSettings() {
  try {
    var res = await fetch(API + '/api/settings', { headers: authHeaders() });
    var data = await res.json();
    var el = document.getElementById('settingsList');
    if (!el) return;
    var settings = data.settings || {};
    var html = '<div class="table-wrapper"><table><tr><th>Key</th><th>Value</th></tr>';
    for (var key in settings) {
      html += '<tr><td>' + key + '</td><td>' + settings[key] + '</td></tr>';
    }
    html += '</table></div>';
    el.innerHTML = html;
  } catch(e) { console.error('loadSettings error:', e); }
}

async function deleteUser(username) {
  if (!confirm('Delete user ' + username + '?')) return;
  try {
    await fetch(API + '/api/users/' + username, {
      method: 'DELETE', headers: authHeaders()
    });
    showToast('User deleted: ' + username, 'success');
    loadUsers();
  } catch(e) { showToast('Error: ' + e.message, 'error'); }
}

