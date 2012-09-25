import org.springframework.stereotype.Repository;
import de.zalando.sprocwrapper.AbstractSProcService;

@Repository
public class {{ interfaceName }}Impl
    extends AbstractSProcService<{{ interfaceName }}, {{ datasourcProvider }}>
    implements {{ interfaceName }} {

    @Autowired
    public {{ interfaceName }}Impl( final {{ datasourcProvider }} p) {
        super(p, {{ interfaceName }}.class);
    }

    {{ functionImplementations }}   
}
