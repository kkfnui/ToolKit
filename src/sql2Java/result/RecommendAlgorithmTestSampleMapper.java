import org.springframework.jdbc.core.RowMapper;
import java.sql.ResultSet;
import java.sql.SQLException;

public class RecommendAlgorithmTestSampleMapper implements RowMapper {
	@Override
	public Object mapRow(ResultSet rs, int rowNum) throws SQLException {
		RecommendAlgorithmTestSample entity = new RecommendAlgorithmTestSample();
		entity.setId(rs.getLong("id"));
		entity.setRecAlgorithmTestId(rs.getLong("rec_algorithm_test_id"));
		entity.setPackageName(rs.getString("package_name"));
		entity.setPackageTitle(rs.getString("package_title"));
		entity.setPackageIcon(rs.getString("package_icon"));
		entity.setPackageInfo(rs.getString("package_info"));
		entity.setPartinNum(rs.getShort("partin_num"));
		entity.setScore(rs.getFloat("score"));
		entity.setCreateBy(rs.getString("create_by"));
		entity.setCreateDatetime(rs.getTimestamp("create_datetime"));
		entity.setUpdateDatetime(rs.getTimestamp("update_datetime"));
		return entity;
	}
}
