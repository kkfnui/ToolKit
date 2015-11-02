import org.springframework.jdbc.core.JdbcTemplate;
import com.xunlei.recommend.web.console.common.QueryResult;
import java.util.List;

public class RecommendAlgorithmTestSampleDao {
	private JdbcTemplate jdbcTemplate;
	public void setJdbcTemplate(JdbcTemplate jdbcTemplate) {this.jdbcTemplate = jdbcTemplate;}
	private static String TABLE_NAME = "test_package_sample";

public RecommendAlgorithmTestSample getById(long id) { 
	String sql = "select * from "+ TABLE_NAME + " where id = ?";
	return (RecommendAlgorithmTestSample) jdbcTemplate.queryForObject(sql, new Object[]{id}, new RecommendAlgorithmTestSampleMapper());
}

public long add(RecommendAlgorithmTestSample entity) {
String sql = "insert into "+ TABLE_NAME + " (" +
	"rec_algorithm_test_id, " +
	"package_name, " +
	"package_title, " +
	"package_icon, " +
	"package_info, " +
	"partin_num, " +
	"score, " +
	"create_by, " +
	"update_datetime)" +
	" values"+
	"(?, ?, ?, ?, ?, ?, ?, ?, ?)";

jdbcTemplate.update(sql, new Object[]{
	entity.getRecAlgorithmTestId(),
	entity.getPackageName(),
	entity.getPackageTitle(),
	entity.getPackageIcon(),
	entity.getPackageInfo(),
	entity.getPartinNum(),
	entity.getScore(),
	entity.getCreateBy(),
	entity.getUpdateDatetime()});

String queryId = "select max(id) from "+TABLE_NAME+" where create_by =?";
long id = jdbcTemplate.queryForObject(
		queryId, new Object[]{entity.getCreateBy()}, Long.class);
return id;
}

public boolean remove(long id) {
	String sql = "delete from "+ TABLE_NAME +" where id = ?";
	int rows = jdbcTemplate.update(sql, new Object[]{id});
	return rows >= 1;
}

public boolean update(RecommendAlgorithmTestSample entity) {
	 String sql = "update "+ TABLE_NAME +
		"set rec_algorithm_test_id=?, "+
		"set package_name=?, "+
		"set package_title=?, "+
		"set package_icon=?, "+
		"set package_info=?, "+
		"set partin_num=?, "+
		"set score=?, "+
		"set create_by=?, "+
		"set create_datetime=?, "+
		"set update_datetime=?, "+
		"where id = ?";

	int rows = jdbcTemplate.update(sql, new Object[]{
		entity.getRecAlgorithmTestId(),
		entity.getPackageName(),
		entity.getPackageTitle(),
		entity.getPackageIcon(),
		entity.getPackageInfo(),
		entity.getPartinNum(),
		entity.getScore(),
		entity.getCreateBy(),
		entity.getCreateDatetime(),
		entity.getUpdateDatetime(),
		entity.getId()});

	return rows >= 1;
}

public QueryResult<RecommendAlgorithmTestSample> getList(int page, int rowNum, String sortBy, String order) {
	int pos = Math.max((page - 1) * rowNum, 0);
	String sql = "select * from "+ TABLE_NAME +" order by " + sortBy + " " + order + " limit " + Integer.toString(pos) + "," + Integer.toString(rowNum);
	List<RecommendAlgorithmTestSample> list = (List<RecommendAlgorithmTestSample>) jdbcTemplate.query(sql, new RecommendAlgorithmTestSampleMapper());	String countSql = "select count(*) from "+ TABLE_NAME ;	int count = jdbcTemplate.queryForObject(countSql, Integer.class);

	QueryResult<RecommendAlgorithmTestSample> result = new QueryResult<RecommendAlgorithmTestSample>(rowNum);
	int totalPage = (count + rowNum -1) / rowNum;
	result.setTotal(totalPage);
	result.setPage(page);
	result.setRecords(count);
	result.setRows(list);

	return result;
}
}
