import org.springframework.stereotype.Repository;
import de.zalando.sprocwrapper.AbstractSProcService;

@Repository
public class {{ interfaceName }}Impl
    extends AbstractSProcService<{{ interfaceName }}, {{ datasourceProvider }}>
    implements {{ interfaceName }} {

    @Autowired
    public {{ interfaceName }}Impl( final {{ datasourceProvider }} p ) {
        super(p, {{ interfaceName }}.class);
    }

{{ functionImplementations }}   
}
